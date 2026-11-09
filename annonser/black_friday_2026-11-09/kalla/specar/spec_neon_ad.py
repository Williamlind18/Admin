import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W.parent / "bfai" / "neon_txt.png").as_uri()
k = 1080 / 1600; x0, y0 = 128, 210
css = f"""
body{{background:#000 url('{BG}') no-repeat;background-size:{1856*k:.1f}px {2304*k:.1f}px;background-position:{-x0*k:.1f}px {-y0*k:.1f}px}}
.sh{{position:absolute;left:0;right:0;bottom:0;height:250px;background:linear-gradient(180deg,rgba(0,0,0,0) 0%,rgba(0,0,0,.8) 50%,rgba(0,0,0,.9) 100%)}}
.t{{position:absolute;left:0;right:0;bottom:44px;text-align:center;color:#fff}}
.h{{font:900 76px/1 'Inter Tight';letter-spacing:-2px}}
.h span{{color:#FFD43B}}
.s{{margin-top:18px;font:700 38px/1 'Inter'}}
.s b{{color:#ff5a64}}
"""
body = """<div class="sh"></div><div class="t"><div class="h">Köp 2 – <span>spara 379 kr</span></div>
<div class="s">Fri frakt · avslutas <b>ikväll 23:59</b></div></div>"""
ADS = [{"out": "../ut_bf/BF_07_neon_4x5.png", "w": 1080, "h": 1350, "css": css, "body": body}]
