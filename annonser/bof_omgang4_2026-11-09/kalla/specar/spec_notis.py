import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W.parent / "ai" / "notis_fix.png").as_uri()
icon = """<div class="ic"><svg width="62" height="62" viewBox="0 0 62 62"><rect width="62" height="62" rx="14" fill="#06BFDD"/>
<text x="27" y="44" font-family="Inter Tight" font-weight="900" font-size="38" fill="#fff" text-anchor="middle">N</text>
<path d="M47 12 l2.2 6 6 2.2 -6 2.2 -2.2 6 -2.2 -6 -6 -2.2 6 -2.2z" fill="#fff"/></svg></div>"""
lock = """<svg width="30" height="38" viewBox="0 0 30 38"><rect x="2" y="16" width="26" height="20" rx="4" fill="#fff"/>
<path d="M8 17 V11 a7 7 0 0 1 14 0 V17" fill="none" stroke="#fff" stroke-width="3.6"/></svg>"""
css = f"""
body{{background:#222 url('{BG}') center/cover no-repeat;font-family:'Inter',sans-serif}}
.dim{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.30) 0%,rgba(0,0,0,.05) 30%,rgba(0,0,0,0) 55%,rgba(0,0,0,.35) 100%)}}
.lock{{position:absolute;left:525px;top:44px}}
.time{{position:absolute;left:0;right:0;top:92px;text-align:center;color:#fff;font:600 236px/1 'Inter Tight';letter-spacing:-6px;
  text-shadow:0 2px 24px rgba(0,0,0,.25)}}
.stack{{position:absolute;left:40px;right:40px;bottom:74px}}
.n{{position:relative;background:rgba(246,246,246,.80);backdrop-filter:blur(30px) saturate(1.6);-webkit-backdrop-filter:blur(30px) saturate(1.6);
  border-radius:44px;padding:26px 34px 28px 120px;margin-top:14px;color:#111;box-shadow:0 8px 30px rgba(0,0,0,.18)}}
.ic{{position:absolute;left:34px;top:34px}}
.hd{{display:flex;justify-content:space-between;align-items:baseline}}
.app{{font:700 33px/1.2 'Inter'}}
.ago{{font:400 29px/1 'Inter';color:#666}}
.ti{{font:700 35px/1.25 'Inter';margin-top:4px}}
.bd{{font:400 33px/1.3 'Inter';margin-top:4px;color:#222}}
.peek{{height:26px;margin:0 30px;background:rgba(235,235,235,.6);border-radius:0 0 30px 30px;backdrop-filter:blur(20px)}}
.bar{{position:absolute;left:390px;width:300px;height:10px;border-radius:5px;background:#fff;bottom:28px;opacity:.9}}
"""
body = f"""<div class="dim"></div><div class="lock">{lock}</div><div class="time">21:47</div>
<div class="stack">
<div class="n">{icon}<div class="hd"><span class="app">Norrtvätt</span><span class="ago">nu</span></div>
<div class="ti">⏳ Höstrean avslutas ikväll 23:59</div>
<div class="bd">Sista chansen: upp till 50 % rabatt + fri frakt.</div></div>
<div class="n">{icon}<div class="hd"><span class="app">Norrtvätt</span><span class="ago">1 tim sedan</span></div>
<div class="ti">Köp 2 – spara 379 kr</div>
<div class="bd">2-pack 619 kr (ord. 998 kr) · räcker i 2 år</div></div>
<div class="peek"></div>
</div><div class="bar"></div>"""
ADS = [{"out": "../ut/SE_22_notisen_4x5.png", "w": 1080, "h": 1350, "css": css, "body": body}]
