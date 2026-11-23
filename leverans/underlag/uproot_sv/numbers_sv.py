#!/usr/bin/env python3
"""Digits in captions (Swedish): 'trettio dagars' -> '30 dagars', 'femtio procent' -> '50 %'."""
import json, re, sys
RULES = [(["femtio", "procent"], "50 %"), (["trettio"], "30"), (["nittonhundra"], "1900")]
UNITS = {"dagar", "dagars", "kronor", "kunder"}
def norm(w): return re.sub(r"[^\wåäöÅÄÖ-]", "", w).lower()
p = sys.argv[1]; W = json.load(open(p, encoding="utf-8")); out = []; i = 0
while i < len(W):
    hit = None
    for seq, rep in RULES:
        n = len(seq)
        if [norm(w["w"]) for w in W[i:i + n]] == seq and len({w["sent"] for w in W[i:i + n]}) == 1: hit = (n, rep); break
    if hit:
        n, rep = hit; tail = re.sub(r"^.*?([.,:;!?]*)$", r"\1", W[i + n - 1]["w"])
        out.append({"w": rep + tail, "start": W[i]["start"], "end": W[i + n - 1]["end"], "sent": W[i]["sent"], "num": True}); i += n
    else:
        out.append(dict(W[i])); i += 1
res = []
for w in out:
    if res and res[-1].get("num") and not re.search(r"[.,:;!?]$", res[-1]["w"]) and norm(w["w"]) in UNITS and w["sent"] == res[-1]["sent"]:
        res[-1]["w"] += " " + w["w"]; res[-1]["end"] = w["end"]; res[-1].pop("num")
    else: res.append(w)
for w in res: w.pop("num", None)
json.dump(res, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(p, [w["w"] for w in res if re.search(r"\d", w["w"])])
