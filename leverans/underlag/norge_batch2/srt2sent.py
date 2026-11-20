"""Swedish caption .srt -> sentence timings (idx, start, end, text), one sentence per line, by end punctuation.
usage: srt2sent.py IN.srt OUT.txt"""
import re, sys
blocks = open(sys.argv[1], encoding="utf-8").read().strip().split("\n\n")
cues = []
for b in blocks:
    L = b.strip().split("\n")
    m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", L[1])
    g = [int(x) for x in m.groups()]
    cues.append((g[0]*3600+g[1]*60+g[2]+g[3]/1000, g[4]*3600+g[5]*60+g[6]+g[7]/1000, " ".join(L[2:]).strip()))
out, cur = [], None
for a, b, t in cues:
    if cur is None: cur = [a, b, t]
    else: cur[1] = b; cur[2] += " " + t
    if re.search(r"[.!?…]\"?$", t):
        out.append(cur); cur = None
if cur: out.append(cur)
with open(sys.argv[2], "w") as f:
    for i, (a, b, t) in enumerate(out):
        f.write(f"{i}\t{a:.2f}\t{b:.2f}\t{t}\n")
print(len(cues), "cues ->", len(out), "sentences")
