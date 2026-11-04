#!/usr/bin/env python3
"""Label ads as Breakthrough, Spend winner, KPI winner or Loser.

Input: a CSV (Ads Manager export) or a JSON list of objects with one row per ad.
Recognised columns (case-insensitive, Swedish and English Ads Manager names work):
  ad name, campaign, spend, purchases, revenue (purchase value), start date or days running,
  and optionally budget_at_launch and budget_now for the scale check.

Example:
  python3 label_ads.py ads.csv --kpi cpa --target 250 --fx 10.5
  python3 label_ads.py ads.json --kpi roas --target 2.0 --json labels.json

The spend threshold comes from the account's monthly spend in USD (see references/labeling.md).
The share is of the ad's campaign spend by default (the four-box rule); use --share-base account
for the Quick Win view (share of the whole account).
Use --fx (account currency per USD) when the account is not in USD, or --threshold to override.
"""
import argparse
import csv
import datetime as dt
import json
import math
import re
import sys

ALIASES = {
    "ad": ["ad", "ad name", "ad_name", "name", "annons", "annonsnamn"],
    "campaign": ["campaign", "campaign name", "campaign_name", "kampanj", "kampanjnamn"],
    "spend": ["spend", "amount spent", "amount_spent", "spent", "spenderat belopp",
              "belopp som spenderats", "kostnad", "ad_spend"],
    "purchases": ["purchases", "website purchases", "conversions", "results", "köp",
                  "webbplatsköp", "resultat", "orders"],
    "revenue": ["revenue", "purchase value", "purchases conversion value", "purchase_value",
                "conversion value", "konverteringsvärde", "konverteringsvärde för köp", "intäkt"],
    "start": ["start", "start date", "start_date", "first_spend_date", "created",
              "created_time", "launch", "launch date", "startdatum", "reporting starts"],
    "days": ["days", "days running", "days_running", "age_days", "dagar"],
    "budget_at_launch": ["budget_at_launch", "budget at launch"],
    "budget_now": ["budget_now", "budget now"],
}

# (upper bound of monthly account spend in USD, share of spend a breakthrough takes)
BRACKETS = [(100_000, 0.30), (250_000, 0.20), (500_000, 0.10), (1_000_000, 0.08), (math.inf, 0.05)]


def norm(s):
    s = re.sub(r"\(.*?\)", "", str(s).lower())  # drop "(SEK)", "(USD)" etc.
    return re.sub(r"[\s_]+", " ", s).strip()


def parse_num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[^\d,.\-]", "", str(v).replace(" ", "").replace(" ", ""))
    if not s or s in "-.,":
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        head, _, tail = s.rpartition(",")
        s = head.replace(",", "") + ("." if len(tail) <= 2 else "") + tail
    try:
        return float(s)
    except ValueError:
        return None


def parse_date(v):
    if not v:
        return None
    s = str(v).strip()[:10]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def load_rows(path):
    if path.lower().endswith(".json"):
        data = json.load(open(path, encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("data") or data.get("ads") or list(data.values())[0]
        return data
    with open(path, encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        return list(csv.DictReader(f, dialect=dialect))


def pick(row, key):
    lookup = {norm(k): v for k, v in row.items()}
    for alias in ALIASES[key]:
        if norm(alias) in lookup and lookup[norm(alias)] not in (None, ""):
            return lookup[norm(alias)]
    return None


def threshold_for(monthly_usd):
    for upper, share in BRACKETS:
        if monthly_usd < upper:
            return share
    return BRACKETS[-1][1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--kpi", choices=["cpa", "roas"], required=True)
    ap.add_argument("--target", type=float, required=True, help="max CPA or min ROAS")
    ap.add_argument("--window-days", type=float, default=30, help="days the export covers (default 30)")
    ap.add_argument("--account-monthly-spend", type=float,
                    help="account spend per month in account currency (default: from the file)")
    ap.add_argument("--fx", type=float, default=1.0, help="account currency units per 1 USD (SEK about 10-11)")
    ap.add_argument("--threshold", type=float, help="override the spend share, e.g. 0.3 or 30")
    ap.add_argument("--share-base", choices=["account", "campaign"], default="campaign",
                    help="campaign = the four-box rule (share of campaign spend after 7 days); account = Quick Win")
    ap.add_argument("--today", help="YYYY-MM-DD for age (default today)")
    ap.add_argument("--min-days", type=float, default=7)
    ap.add_argument("--json", help="also write the labels to this JSON file")
    a = ap.parse_args()

    today = parse_date(a.today) if a.today else dt.date.today()
    ads = []
    for row in load_rows(a.file):
        spend = parse_num(pick(row, "spend")) or 0.0
        ad = {
            "ad": str(pick(row, "ad") or "?"),
            "campaign": str(pick(row, "campaign") or ""),
            "spend": spend,
            "purchases": parse_num(pick(row, "purchases")),
            "revenue": parse_num(pick(row, "revenue")),
            "budget_at_launch": parse_num(pick(row, "budget_at_launch")),
            "budget_now": parse_num(pick(row, "budget_now")),
        }
        days = parse_num(pick(row, "days"))
        start = parse_date(pick(row, "start"))
        if days is None and start:
            days = (today - start).days
        ad["days"] = days
        ads.append(ad)
    if not ads:
        sys.exit("No rows found.")

    total = sum(x["spend"] for x in ads)
    monthly = a.account_monthly_spend or total * 30.0 / a.window_days
    monthly_usd = monthly / a.fx
    thr = a.threshold if a.threshold is not None else threshold_for(monthly_usd)
    if thr > 1:
        thr /= 100.0
    camp_tot = {}
    for x in ads:
        camp_tot[x["campaign"]] = camp_tot.get(x["campaign"], 0.0) + x["spend"]

    for x in ads:
        base = camp_tot[x["campaign"]] if a.share_base == "campaign" else total
        x["share"] = x["spend"] / base if base else 0.0
        if a.kpi == "cpa":
            p = x["purchases"] or 0
            x["kpi_value"] = x["spend"] / p if p else math.inf
            x["kpi_ok"] = x["kpi_value"] <= a.target
        else:
            r = x["revenue"] or 0
            x["kpi_value"] = r / x["spend"] if x["spend"] else 0.0
            x["kpi_ok"] = x["kpi_value"] >= a.target
        notes = []
        big = x["share"] >= thr
        if x["days"] is not None and x["days"] < a.min_days:
            box = "Too early"
        elif big and x["kpi_ok"]:
            box = "Breakthrough"
            if x["budget_at_launch"] and x["budget_now"]:
                x["scale"] = x["budget_now"] / x["budget_at_launch"]
                if x["scale"] <= 1.0:
                    notes.append("budget not raised yet: confirm scale")
            else:
                notes.append("scale unknown: check that the budget rose after launch")
        elif big:
            box = "Spend winner"
        elif x["kpi_ok"]:
            box = "KPI winner"
        else:
            box = "Loser"
        if x["days"] is None:
            notes.append("age unknown")
        x["box"] = box
        x["note"] = "; ".join(notes)

    ads.sort(key=lambda x: -x["spend"])
    print(f"Account spend in file: {total:,.0f} over {a.window_days:g} days "
          f"-> about {monthly:,.0f}/month ({monthly_usd:,.0f} USD at fx {a.fx:g}).")
    print(f"Spend threshold for a breakthrough: {thr:.0%} of {a.share_base} spend. "
          f"KPI: {a.kpi.upper()} {'<=' if a.kpi == 'cpa' else '>='} {a.target:g}.\n")
    print("| Ad | Campaign | Spend | Share | " + a.kpi.upper() + " | Days | Box | Note |")
    print("|---|---|---|---|---|---|---|---|")
    for x in ads:
        kv = "-" if math.isinf(x["kpi_value"]) else f"{x['kpi_value']:.2f}"
        d = "?" if x["days"] is None else f"{x['days']:g}"
        print(f"| {x['ad']} | {x['campaign']} | {x['spend']:,.0f} | {x['share']:.0%} | {kv} | {d} | "
              f"{x['box']} | {x['note']} |")
    counts = {}
    for x in ads:
        counts[x["box"]] = counts.get(x["box"], 0) + 1
    print("\n" + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    if a.json:
        out = [{k: (None if isinstance(v, float) and math.isinf(v) else v) for k, v in x.items()} for x in ads]
        json.dump({"threshold": thr, "monthly_spend": monthly, "monthly_spend_usd": monthly_usd,
                   "ads": out}, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
