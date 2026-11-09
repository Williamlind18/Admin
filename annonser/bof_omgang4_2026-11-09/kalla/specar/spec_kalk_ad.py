import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W.parent / "ai" / "kalk_lcd.png").as_uri()
css = f"""
body{{background:#ddd url('{BG}') center bottom/cover no-repeat}}
.shade{{position:absolute;left:0;top:0;width:1080px;height:640px;background:linear-gradient(180deg,rgba(255,255,255,.80) 0%,rgba(255,255,255,.62) 62%,rgba(255,255,255,0) 100%)}}
.t{{position:absolute;left:64px;right:64px;top:62px;color:#111}}
.pill{{display:inline-block;background:#E31B23;color:#fff;font:800 30px/1 'Inter';letter-spacing:.5px;padding:14px 22px;border-radius:999px}}
.h{{margin-top:26px;font:900 112px/.98 'Inter Tight';letter-spacing:-4px}}
.h span{{color:#E31B23}}
.s{{margin-top:26px;font:600 38px/1.3 'Inter';color:#222}}
.s b{{font-weight:800}}
.s s{{color:#777;text-decoration-thickness:3px}}
"""
body = """<div class="shade"></div><div class="t">
<div class="pill">HÖSTREA · SLUTAR IKVÄLL 23:59</div>
<div class="h">Köp 2 och<br><span>spara 379 kr</span></div>
<div class="s"><b>2-pack 619 kr</b> <s>998 kr</s> · fri frakt</div></div>"""
ADS = [{"out": "../ut/SE_20_kalkylatorn_4x5.png", "w": 1080, "h": 1350, "css": css, "body": body}]
