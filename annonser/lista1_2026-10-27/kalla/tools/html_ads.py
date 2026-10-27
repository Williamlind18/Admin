"""Render HTML statics to PNG with headless Chrome. Text is always set here, never by an image model.
Usage: html_ads.py SPEC.py   (SPEC defines ADS = [{"out", "w", "h", "css", "body"}])"""
import pathlib, runpy, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
CHROME = str(HERE / "chrome.sh")
FONTS = (HERE.parent / "fonts" / "all.css").as_uri()
FIT = """<script>document.fonts.ready.then(()=>{document.querySelectorAll('.fit').forEach(el=>{
let s=parseFloat(getComputedStyle(el).fontSize);while(el.scrollWidth>el.clientWidth+1&&s>10){s*=.97;el.style.fontSize=s+'px';}});});</script>"""


def render(ad, base):
    w, h = ad["w"], ad["h"]
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>@import url("{FONTS}");'
            f'*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:{w}px;height:{h}px;overflow:hidden}}'
            f'body{{position:relative;-webkit-font-smoothing:antialiased}}.fit{{white-space:nowrap}}{ad["css"]}</style></head>'
            f'<body>{ad["body"]}{FIT}</body></html>')
    out = (base / ad["out"]).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    src = out.parent / "_html" / (out.stem + ".html")
    src.parent.mkdir(exist_ok=True)
    src.write_text(html, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--window-size={w},{h}", "--virtual-time-budget=7000", f"--screenshot={out}", src.as_uri()],
                   check=True, capture_output=True)
    print("ok", out)


if __name__ == "__main__":
    spec = pathlib.Path(sys.argv[1]).resolve()
    only = sys.argv[2:]
    for ad in runpy.run_path(str(spec))["ADS"]:
        if not only or any(o in ad["out"] for o in only):
            render(ad, spec.parent)
