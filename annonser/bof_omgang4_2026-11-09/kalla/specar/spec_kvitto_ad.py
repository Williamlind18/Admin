import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W.parent / "ai" / "kvitto2_txt.png").as_uri()
k = 1080 / 1300
css = f"""
body{{background:#eee url('{BG}') no-repeat;background-size:{1856*k:.1f}px {2304*k:.1f}px;background-position:{-556*k:.1f}px {-679*k:.1f}px}}
.t{{position:absolute;left:500px;width:540px;top:46px;text-align:center;color:#141414}}
.a{{font:900 66px/1 'Inter Tight';letter-spacing:-1px}}
.p{{font:900 200px/.9 'Inter Tight';letter-spacing:-8px;color:#E31B23;margin:6px 0 2px}}
.d{{display:inline-block;margin-top:22px;background:#141414;color:#fff;font:700 31px/1.25 'Inter';padding:14px 24px;border-radius:12px}}
.d b{{color:#FFD43B}}
"""
body = """<div class="t"><div class="a">UPP TILL</div><div class="p">50 %</div><div class="a">RABATT</div>
<div class="d">Höstrean avslutas<br><b>ikväll 23:59</b></div></div>"""
ADS = [{"out": "../ut/SE_21_kvittot_foto_4x5.png", "w": 1080, "h": 1350, "css": css, "body": body}]
