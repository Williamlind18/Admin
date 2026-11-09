import re, sys, hashlib, pathlib, urllib.request
out = pathlib.Path(sys.argv[1]); fams = sys.argv[2:]
ua = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
url = "https://fonts.googleapis.com/css2?" + "&".join("family=" + f for f in fams) + "&display=swap"
css = urllib.request.urlopen(urllib.request.Request(url, headers=ua)).read().decode()
blocks = re.findall(r"/\* ([^*]+) \*/\s*(@font-face \{[^}]+\})", css)
keep = []
for sub, b in blocks:
    if sub.strip() not in ("latin", "latin-ext"): continue
    u = re.search(r"url\((https://[^)]+)\)", b).group(1)
    name = hashlib.md5(u.encode()).hexdigest()[:12] + ".woff2"
    p = out / name
    if not p.exists(): p.write_bytes(urllib.request.urlopen(urllib.request.Request(u, headers=ua)).read())
    keep.append(f"/* {sub} */\n" + b.replace(u, p.as_uri()))
with open(out / "all.css", "a") as f: f.write("\n" + "\n".join(keep) + "\n")
print(len(keep), "faces")
