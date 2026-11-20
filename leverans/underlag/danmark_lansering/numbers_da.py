#!/usr/bin/env python3
"""Show money, percentages and larger counts as digits in words_global.json (Danish)."""
import json, re, sys
RULES = [
    (["ni", "hundrede", "og", "nioghalvfems"], "999"),
    (["seks", "hundrede", "og", "nitten"], "619"),
    (["hundrede", "og", "halvfems"], "190"),
    (["hundrede", "og", "firs"], "180"),
    (["nioghalvfems", "procent"], "99 %"),
    (["firs", "procent"], "80 %"),
    (["tyve", "procent"], "20 %"),
    (["femogtyve"], "25"),
    (["tres"], "60"),
    (["nitten", "hundrede", "og", "fire"], "1904"),
    (["nittenhundredetallet"], "1900-tallet"),
    (["to", "hundrede", "og", "halvtreds"], "250"),
    (["fyrre", "procent"], "40 %"),
    (["femten", "tusind"], "15.000"),
    (["seks", "tusind"], "6.000"),
    (["to", "hundrede"], "200"),
    (["halvtreds", "procent"], "50 %"),
    (["tusind"], "1.000"),
    (["tredive"], "30"),
    (["nitten"], "19"),
    (["tyve"], "20"),
]
UNITS = {"kroner", "dage", "dages", "sekunder", "år", "kunder"}
def norm(w): return re.sub(r"[^\wæøåÆØÅ-]", "", w).lower()
def main(path):
    W = json.load(open(path, encoding="utf-8"))
    out, i = [], 0
    while i < len(W):
        hit = None
        for seq, rep in RULES:
            n = len(seq)
            if i + n <= len(W) and [norm(w["w"]) for w in W[i:i + n]] == seq and len({w["sent"] for w in W[i:i + n]}) == 1:
                hit = (n, rep); break
        if hit:
            n, rep = hit
            last = W[i + n - 1]["w"]
            tail = re.sub(r"^.*?([.,:;!?]*)$", r"\1", last)
            first = W[i]["w"]
            out.append({"w": rep + tail, "start": W[i]["start"], "end": W[i + n - 1]["end"], "sent": W[i]["sent"], "num": True})
            i += n
        else:
            out.append(dict(W[i])); i += 1
    # keep a number together with its unit
    res = []
    for w in out:
        if res and res[-1].get("num") and not re.search(r"[.,:;!?]$", res[-1]["w"]) and norm(w["w"]) in UNITS and w["sent"] == res[-1]["sent"]:
            res[-1]["w"] += " " + w["w"]; res[-1]["end"] = w["end"]; res[-1].pop("num")
        else:
            res.append(w)
    for w in res: w.pop("num", None)
    json.dump(res, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(path, len(W), "->", len(res), [w["w"] for w in res if re.search(r"\d", w["w"])])
main(sys.argv[1])
