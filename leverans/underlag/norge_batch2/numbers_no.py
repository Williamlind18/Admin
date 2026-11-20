#!/usr/bin/env python3
"""Show money, percentages and counts >= 10 as digits in words_global.json (Norwegian). Thousands use a no-break space."""
import json, re, sys
NB = " "
RULES = [
    (["ni", "hundre", "og", "nittini"], "999"),
    (["flere", "tusen"], "KEEP"),
    (["femten", "tusen"], f"15{NB}000"),
    (["seks", "tusen"], f"6{NB}000"),
    (["to", "hundre"], "200"),
    (["over", "tusen"], None),          # handled below: keep "over", turn "tusen" into 1 000
    (["femti", "prosent"], "50 %"),
    (["tjue", "prosent"], "20 %"),
    (["tretti"], "30"),
    (["nitten"], "19"),
    (["tolv"], "12"),
    (["femti"], "50"),
    (["seksti"], "60"),
    (["tusen"], f"1{NB}000"),
]
UNITS = {"kroner", "dager", "dagers", "sekunder", "år", "kunder", "tabletter", "maskiner"}
def norm(w): return re.sub(r"[^\wæøåÆØÅ-]", "", w).lower()
def main(path):
    W = json.load(open(path, encoding="utf-8"))
    out, i = [], 0
    while i < len(W):
        hit = None
        for seq, rep in RULES:
            if rep is None:
                continue
            n = len(seq)
            if i + n <= len(W) and [norm(w["w"]) for w in W[i:i + n]] == seq and len({w["sent"] for w in W[i:i + n]}) == 1:
                hit = (n, rep); break
        if hit and hit[1] == "KEEP":
            out += [dict(w) for w in W[i:i + hit[0]]]; i += hit[0]; continue
        if hit:
            n, rep = hit
            tail = re.sub(r"^.*?([.,:;!?]*)$", r"\1", W[i + n - 1]["w"])
            out.append({"w": rep + tail, "start": W[i]["start"], "end": W[i + n - 1]["end"], "sent": W[i]["sent"], "num": True})
            i += n
        else:
            out.append(dict(W[i])); i += 1
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
