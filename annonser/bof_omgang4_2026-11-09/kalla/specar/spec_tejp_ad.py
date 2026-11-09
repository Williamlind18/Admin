import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W.parent / "ai" / "tejp_tape.png").as_uri()
css = f"""
body{{background:#ccc url('{BG}') no-repeat;background-size:1350.2px 1676.2px;background-position:-155px -150px}}
.t{{position:absolute;left:40px;right:40px;top:44px;text-align:center;color:#141414}}
.pill{{display:inline-block;background:#141414;color:#fff;font:800 32px/1 'Inter';letter-spacing:.3px;padding:16px 26px;border-radius:999px}}
.pill b{{color:#FFD43B}}
.h{{margin-top:28px;font:900 100px/.98 'Inter Tight';letter-spacing:-3.5px}}
.s{{margin-top:22px;font:700 40px/1.2 'Inter';color:#1d1d1d}}
.s span{{color:#E31B23}}
.foot{{position:absolute;left:0;right:0;bottom:64px;text-align:center}}
.chip{{display:inline-block;background:rgba(255,255,255,.92);color:#141414;font:700 33px/1 'Inter';padding:18px 28px;border-radius:14px;box-shadow:0 6px 20px rgba(0,0,0,.15)}}
"""
body = """<div class="t"><div class="pill">HÖSTREAN SLUTAR <b>IKVÄLL 23:59</b></div>
<div class="h">Sista kvällen<br>på höstrean</div>
<div class="s"><span>Köp 2 – spara 379 kr</span> · fri frakt</div></div>
<div class="foot"><div class="chip">✓ 30 dagars pengarna-tillbaka-garanti</div></div>"""
ADS = [{"out": "../ut/SE_23_reatejp_4x5.png", "w": 1080, "h": 1350, "css": css, "body": body}]
