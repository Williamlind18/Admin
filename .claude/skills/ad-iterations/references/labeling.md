# Labeling winners and naming ads

## The four variables
| Variable | Measures | Notes |
|---|---|---|
| KPI | CPA or ROAS against the brand's target | Judge it after 7 days. |
| Spend | The ad's share of spend | The more spend Meta gives it, the more it wins. |
| Scale | How much the ad let the account raise its budget | Few people track this one. Compare the daily budget before the ad launched with the budget it holds 1-3 weeks later. |
| Time | How long it keeps running and holding spend | Longer is better. |

## The four boxes
The slide's exact rule: the ad gets "10-30%+ of camp spend" after 7 days, so the share is of its
**campaign's** spend. The Quick Win doc instead uses the share of the whole account's spend over the last
30 days. `label_ads.py` uses campaign share by default and account share with `--share-base account`.

- **Loser:** below the spend threshold and misses KPI after 7 days. A flop.
- **KPI winner:** hits KPI after 7 days but stays below the spend threshold. Results without spend.
  Many people call this a winner. In this system it does not count, because it scales nothing.
- **Spend winner:** at or above the spend threshold but misses KPI. Spend without results.
- **Breakthrough:** at or above the spend threshold, hits KPI and lets you raise the budget.

Each box points to a different way to iterate (see `recipes.md`).

## The spend threshold
Found from a script over many accounts. The smaller the account, the bigger share a winner takes.

| Account spend per month (USD) | Breakthrough share of spend | `label_ads.py` uses |
|---|---|---|
| 0–100k | 30–60 % | 30 % |
| 100k–250k | 20–50 % | 20 % |
| 250k–500k | 10–30 % | 10 % |
| 500k–1M | 8–15 % | 8 % |
| 1M–2M+ | 5–10 % | 5 % |

Convert the account's monthly spend to USD at today's rate before picking the row (pass `--fx`, the
account currency per USD, e.g. about 10-11 for SEK). The script uses the lower end of each range.

## Testing campaigns (CBO)
- Test in CBO. The share-of-spend rule is usually read inside a CBO. ABO works too, as a preference.
- An ad that hits KPI in testing but has not pulled spend is labeled breakthrough only after it
  moves to the scaling campaign and pulls spend there.
- Ads younger than 7 days are "too early".

## Getting the numbers
Read-only. Never change budgets, statuses or campaigns while labeling.

1. **Meta Ads connector** (if connected): find the account with `ads_get_ad_accounts`, then read
   ad-level insights for the last 30 days with `ads_get_ad_entities`. You need spend, purchases,
   purchase value or ROAS, the campaign and the ad's created or start date. Check field names with
   `ads_get_field_context` first. Save the rows as JSON and run the script.
2. **Trackpanda connector** (if connected): `get_store_overview` for currency and timezone, then
   `get_ad_performance` for spend, orders and revenue per ad. Trackpanda's numbers are profit-based,
   so state which source you used.
3. **Manual export:** ask for an Ads Manager export at ad level, last 30 days, with the columns Ad
   name, Campaign name, Amount spent, Purchases (or Results), Purchase conversion value and Reporting
   starts or Created. Swedish column names work.

Then run:

```bash
python3 scripts/label_ads.py ads.csv --kpi cpa --target 300 --fx 10.6
python3 scripts/label_ads.py ads.json --kpi roas --target 2.0 --share-base campaign --json labels.json
```

Add the columns `budget_at_launch` and `budget_now` if you know them; otherwise the script notes that
scale must be confirmed for each breakthrough. Ask the user what they consider their KPI target if the
brand file does not say.

## Competitors
- Meta Ad Library (the `ads_library_search` tool if available, or the user's screenshots). Signs of a
  winner: it has run for months, the brand keeps making new versions of it, and it has many active
  copies.
- Ad Spy-type tools: sort by shares. Meta also shows impressions for some ads.
- A competitor's top ad cannot be labeled exactly, so say how confident you are.

## Naming scheme
The point is to see at a glance how many iterations each test has and how they did.

The talk's scheme ("Batch#5 Iter#2-Batch#3", 8:18):
- Every new test or concept gets the **next free batch number**, never reused.
- An iteration also carries a **pointer to its parent**: `I2-B03` is the second iteration of batch 3.
  So "Batch#5 Iter#2-Batch#3" is batch 5, which is iteration 2 of batch 3.
- A brand-new concept has no I part.
- Then you can ask "how many iterations have we made on our breakthroughs?" by counting the ads that
  point to each breakthrough.

Recommended name (keeps Ads Manager sortable and filterable):

```
B12 | I2-B03 | angle | authority | awareness | format | H1
B12 | I2-B03 | mold-free | list | unaware | ai-vo | H1
```

`H1-H3` are the three hooks of the same concept. Add a language suffix such as `-NO` for translated
versions of the same ad. Put a brand prefix first if one Ads Manager account runs several brands; the
agency filters on it ("Ad name contains EAM").

The agency's long version, as shown in the talk:
`EAM BATCH#96 … (BATCH#89 iteration) - ITER#2 - LP: Quiz Funnel - Static - Valter - Kat - V3 - C#21, #27 - H#6, #7 - Whitelist Page`
= brand prefix, batch 96, iteration 2 of batch 89, landing page "Quiz Funnel", format static, two people
(maker and strategist), version 3, concepts 21 and 27, hooks 6 and 7, run from a whitelisted page.
