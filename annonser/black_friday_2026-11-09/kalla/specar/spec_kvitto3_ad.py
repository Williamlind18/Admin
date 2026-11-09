import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W.parent / "bfai" / "kvitto3_fix.png").as_uri()
k = 1080 / 1296; x0, y0 = 560, 684
css = f"""
body{{background:#ddd url('{BG}') no-repeat;background-size:{1856*k:.1f}px {2304*k:.1f}px;background-position:{-x0*k:.1f}px {-y0*k:.1f}px}}
.card{{position:absolute;left:560px;top:60px;width:470px;background:#0b0b0b;color:#fff;border-radius:22px;padding:34px 30px 32px;text-align:center;
  box-shadow:0 18px 40px rgba(0,0,0,.35);transform:rotate(2deg)}}
.a{{font:900 66px/1 'Inter Tight';letter-spacing:-1px}}
.b{{font:900 54px/1 'Inter Tight';color:#FFD43B;margin-top:16px;letter-spacing:-1px}}
.b big{{display:block;font-size:150px;letter-spacing:-6px;line-height:1}}
.c{{font:700 32px/1.25 'Inter';margin-top:16px;color:#eee}}
.c b{{color:#ff5a64}}
"""
body = """<div class="card"><div class="a">BLACK FRIDAY</div><div class="b">UPP TILL<big>50 %</big>RABATT</div>
<div class="c">Avslutas <b>ikväll 23:59</b></div></div>"""
ADS = [{"out": "../ut_bf/BF_02_kvittot_foto_4x5.png", "w": 1080, "h": 1350, "css": css, "body": body}]
