import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W.parent / "bfai" / "ros3_fix2.png").as_uri()
css = f"""
body{{background:#222 url('{BG}') center/cover no-repeat}}
.t{{position:absolute;left:0;right:0;top:56px;text-align:center;color:#fff}}
.k{{display:inline-block;font:800 34px/1 'Inter';letter-spacing:6px;color:#111;background:#FFD43B;padding:14px 24px;border-radius:8px}}
.h{{margin-top:22px;font:900 150px/1 'Inter Tight';letter-spacing:-6px}}
.s{{margin-top:12px;font:700 40px/1.2 'Inter';color:#e8e8e8}}
.s s{{color:#aaa;text-decoration-thickness:3px}}
.s b{{color:#FFD43B}}
.f{{position:absolute;left:0;right:0;bottom:64px;text-align:center;color:#fff;font:800 44px/1 'Inter Tight'}}
.f span{{color:#ff5a64}}
"""
body = """<div class="t"><div class="k">BLACK FRIDAY</div><div class="h">2 för 619 kr</div>
<div class="s"><s>998 kr</s> · <b>du sparar 379 kr</b></div></div>
<div class="f">Fri frakt · avslutas <span>ikväll 23:59</span></div>"""
ADS = [{"out": "../ut_bf/BF_09_paketet_4x5.png", "w": 1080, "h": 1350, "css": css, "body": body}]
