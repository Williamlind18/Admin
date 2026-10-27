#!/usr/bin/env python3
"""Renderar BOF-statics: text sätts i HTML och fotograferas med headless Chrome/Edge/Chromium.

Kör:  python3 render.py annonser.json
annonser.json = en lista med annonser, se ../references/formats.md. Sökvägar är relativa till json-filen.
Textfält får innehålla HTML (<br>, <b>, <u>, <span class='big'>). Skriv & som &amp;.
"""
import json, os, pathlib, shutil, subprocess, sys

FONTS = ("https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800;900"
         "&family=Oswald:wght@600;700&family=Poppins:wght@600;700;800;900&family=Patrick+Hand&display=swap")

# Krymper .fit-element (en rad) tills de får plats i sin bredd.
FIT_JS = """<script>document.fonts.ready.then(()=>{document.querySelectorAll('.fit').forEach(el=>{
let s=parseFloat(getComputedStyle(el).fontSize);while(el.scrollWidth>el.clientWidth+1&&s>12){s*=.97;el.style.fontSize=s+'px';}});
document.body.dataset.ready=1;});</script>"""

PLACEHOLDER_BG = "linear-gradient(160deg,#9aa3ad 0%,#5f6873 60%,#3f464f 100%)"
PLACEHOLDER_PRODUCT = ("<div style=\"position:absolute;inset:0;border:6px dashed rgba(0,0,0,.35);border-radius:28px;display:flex;"
                       "align-items:center;justify-content:center;font:800 40px Poppins;color:rgba(0,0,0,.4)\">PRODUKT</div>")


def page(w, h, css, body, ad):
    fonts = ad.get("fonts", FONTS)
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>@import url("{fonts}");'
            f':root{{--accent:{ad.get("accent", "#E31B23")};--ink:{ad.get("ink", "#111111")}}}'
            f'*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:{w}px;height:{h}px;overflow:hidden}}'
            f'body{{position:relative;font-family:"Poppins",sans-serif;-webkit-font-smoothing:antialiased}}'
            f'.bg{{position:absolute;inset:0;background-repeat:no-repeat}}.fit{{white-space:nowrap}}{css}</style></head>'
            f'<body>{body}{FIT_JS}</body></html>')


def bg_css(ad, fallback=PLACEHOLDER_BG):
    return f"url('{ad['_bg']}') center/cover no-repeat" if ad.get("_bg") else fallback


def product(ad, css_box, effect="filter:drop-shadow(0 22px 30px rgba(0,0,0,.35))"):
    if ad.get("_product"):
        return (f'<div style="position:absolute;{css_box};background:url(\'{ad["_product"]}\') center/contain no-repeat;{effect}"></div>')
    return f'<div style="position:absolute;{css_box}">{PLACEHOLDER_PRODUCT}</div>'


# ---------- Brevet: "Nu säger vi farväl" (4:5) ----------
def brev(ad, t):
    paper = "#F5F2EB"
    css = f"""body{{background:{bg_css(ad, paper)}}}
    h1{{position:absolute;left:90px;top:165px;width:900px;font-family:'Inter';font-weight:800;font-size:104px;letter-spacing:-.035em;
        line-height:1.05;color:var(--ink)}}
    .body{{position:absolute;left:92px;top:350px;width:540px;font-family:'Inter';font-size:39px;line-height:54px;color:var(--ink)}}
    .body p{{margin-bottom:36px}} .body b{{font-weight:800}} .sig{{font-style:italic}}"""
    paras = "".join(f"<p>{p}</p>" for p in t["stycken"])
    sig = f'<p class="sig">{t["signatur"]}</p>' if t.get("signatur") else ""
    # Produktfoto på vit bakgrund smälter in i papperet med multiply; frilagd PNG får skugga.
    effect = "filter:drop-shadow(0 22px 30px rgba(0,0,0,.35))" if ad.get("produkt_frilagd") else "mix-blend-mode:multiply"
    body = (f'<h1 class="fit">{t["rubrik"]}</h1><div class="body">{paras}{sig}</div>'
            + product(ad, "left:652px;top:430px;width:400px;height:880px", effect))
    return 1080, 1350, page(1080, 1350, css, body, ad)


# ---------- Rea-skylten: "UPP TILL 50% / SISTA CHANSEN" (4:5) ----------
def rea(ad, t):
    css = f""".bg{{background:{bg_css(ad)}}}
    .shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.45),rgba(0,0,0,.15) 38%,rgba(0,0,0,0) 50%)}}
    .red{{position:absolute;left:86px;right:86px;top:40px;background:var(--accent);text-align:center;color:#fff;padding:18px 24px 26px;line-height:1}}
    .red small{{display:block;font-weight:800;font-size:58px;letter-spacing:.02em}}
    .red b{{display:block;font-weight:800;font-size:138px;letter-spacing:-.025em;margin-top:6px}}
    .box{{position:absolute;left:50%;transform:translateX(-50%);top:316px;background:#fff;color:#000;font-weight:800;font-size:54px;
          padding:4px 30px;border:3px solid #000;line-height:1.1;white-space:nowrap}}
    .sub{{position:absolute;left:50%;transform:translateX(-50%);top:396px;white-space:nowrap;text-align:center;color:#fff;font-weight:600;
          font-size:31px;line-height:1.2;background:rgba(0,0,0,.45);padding:6px 18px;border-radius:10px}}"""
    sub = f'<div class="sub">{t["under"]}</div>' if t.get("under") else ""
    body = (f'<div class="bg"></div><div class="shade"></div><div class="red"><small class="fit">{t["upp"]}</small>'
            f'<b class="fit">{t["stor"]}</b></div><div class="box">{t["ruta"]}</div>{sub}')
    return 1080, 1350, page(1080, 1350, css, body, ad)


# ---------- Slutsåld: "SLUTSÅLD TVÅ GÅNGER / DIN SISTA CHANS" (1:1) ----------
def slutsald(ad, t):
    ad.setdefault("ink", "#1B3352")
    css = f""".bg{{background:{bg_css(ad)}}}
    .haze{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,.78) 0%,rgba(255,255,255,.45) 34%,rgba(255,255,255,0) 52%)}}
    .t{{position:absolute;left:40px;right:40px;top:40px;text-align:center;color:var(--ink);font-family:'Oswald';line-height:1.02}}
    .t .a{{font-weight:700;font-size:104px}} .t .b{{font-weight:600;font-size:60px;margin-top:6px}}
    .t .b u{{text-decoration-thickness:5px;text-underline-offset:8px}}
    .t .c{{display:inline-block;max-width:100%;font-family:'Poppins';font-weight:800;font-size:34px;color:#fff;background:var(--accent);
           margin-top:22px;padding:10px 26px;border-radius:999px}}"""
    body = (f'<div class="bg"></div><div class="haze"></div><div class="t"><div class="a fit">{t["rubrik"]}</div>'
            f'<div class="b fit">{t["under"]} <u>{t["under_markerad"]}</u></div><div class="c fit">{t["pill"]}</div></div>')
    return 1080, 1080, page(1080, 1080, css, body, ad)


# ---------- Post-it-lappar (4:5) ----------
def postit(ad, t):
    spots = [tuple(x) for x in ad.get("spots", [(52, 300, -3), (712, 640, 2), (70, 940, -1.5)])]  # (left, top, deg)
    notes = "".join(f'<div class="note" style="left:{x}px;top:{y}px;transform:rotate({r}deg)">{n}</div>'
                    for (x, y, r), n in zip(spots, t["lappar"]))
    css = f""".bg{{background:{bg_css(ad)}}}
    .note{{position:absolute;width:320px;min-height:300px;background:#F2E38A;font-family:'Patrick Hand';color:#1d1d1d;font-size:52px;
           line-height:1.12;padding:30px 26px;box-shadow:0 10px 18px rgba(0,0,0,.18),0 2px 4px rgba(0,0,0,.12)}}
    .note .big{{font-size:58px;color:var(--accent)}}"""
    return 1080, 1350, page(1080, 1350, css, f'<div class="bg"></div>{notes}', ad)


# ---------- Vi säger hejdå (4:5) ----------
def hejda(ad, t):
    css = """body{background:radial-gradient(ellipse at 50% 48%,color-mix(in srgb,var(--accent) 80%,#ff5a5a) 0%,var(--accent) 38%,
             color-mix(in srgb,var(--accent) 62%,#000) 100%)}
    .brand{position:absolute;left:0;right:0;top:62px;text-align:center;color:#fff;font-weight:700;font-size:40px;letter-spacing:.24em}
    .w{position:absolute;left:40px;right:40px;text-align:center;color:#fff;font-weight:900;letter-spacing:-.03em;line-height:1}
    .w1{top:156px;font-size:166px} .w2{top:978px;font-size:196px}
    .sub{position:absolute;left:40px;right:40px;top:1176px;text-align:center;color:#fff;font-weight:700;font-size:40px}"""
    brand = f'<div class="brand">{ad["brand"]}</div>' if ad.get("brand") else ""
    body = (f'{brand}<div class="w w1 fit">{t["ord1"]}</div><div class="w w2 fit">{t["ord2"]}</div>'
            + product(ad, "left:50%;transform:translateX(-50%);top:318px;width:560px;height:606px")
            + f'<div class="sub fit">{t["under"]}</div>')
    return 1080, 1350, page(1080, 1350, css, body, ad)


FORMATS = {"brev": brev, "rea": rea, "slutsald": slutsald, "postit": postit, "hejda": hejda}


def find_chrome():
    cands = [os.environ.get("CHROME"),
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium",
             "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
    cands += [shutil.which(n) for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge")]
    for c in cands:
        if c and pathlib.Path(c).exists():
            return c
    sys.exit("Hittar ingen Chrome/Edge/Chromium. Installera Chrome eller sätt miljövariabeln CHROME till sökvägen.")


def main(spec_path):
    spec_path = pathlib.Path(spec_path).resolve()
    base, chrome = spec_path.parent, find_chrome()
    for ad in json.loads(spec_path.read_text(encoding="utf-8")):
        for key in ("bg", "product"):
            if ad.get(key):
                p = (base / ad[key]).resolve()
                if not p.exists():
                    sys.exit(f"Bilden finns inte: {p}")
                ad["_" + key] = p.as_uri()
        w, h, html = FORMATS[ad["format"]](ad, ad["text"])
        out = (base / ad["out"]).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        src = out.parent / "_html" / (out.stem + ".html")
        src.parent.mkdir(exist_ok=True)
        src.write_text(html, encoding="utf-8")
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={w},{h}", "--virtual-time-budget=6000", f"--screenshot={out}", src.as_uri()],
                       check=True, capture_output=True)
        print("ok", out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
