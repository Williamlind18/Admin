import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W.parent / "bfai" / "kasse_txt.png").as_uri()
k = 1080 / 1400; x0, y0 = 250, 300
css = f"""
body{{background:#eee url('{BG}') no-repeat;background-size:{1856*k:.1f}px {2304*k:.1f}px;background-position:{-x0*k:.1f}px {-y0*k:.1f}px}}
.t{{position:absolute;left:40px;right:40px;top:34px;text-align:center;color:#111}}
.h{{font:900 92px/1 'Inter Tight';letter-spacing:-3px}}
.h span{{color:#E31B23}}
.s{{display:inline-block;margin-top:16px;background:#111;color:#fff;font:700 33px/1 'Inter';padding:14px 22px;border-radius:10px}}
.s b{{color:#FFD43B}}
"""
body = """<div class="t"><div class="h fit">Köp 2 – <span>spara 379 kr</span></div>
<div class="s">Black Friday · fri frakt · avslutas <b>ikväll 23:59</b></div></div>"""
ADS = [{"out": "../ut_bf/BF_06_kassen_4x5.png", "w": 1080, "h": 1350, "css": css, "body": body}]
