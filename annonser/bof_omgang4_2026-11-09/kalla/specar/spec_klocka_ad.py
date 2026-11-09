import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W.parent / "ai" / "klocka_lcd.png").as_uri()
css = f"""
body{{background:#111 url('{BG}') center/cover no-repeat}}
.shade{{position:absolute;left:0;top:0;width:1080px;height:760px;background:linear-gradient(180deg,rgba(0,0,0,.72) 0%,rgba(0,0,0,.55) 60%,rgba(0,0,0,0) 100%)}}
.t{{position:absolute;left:60px;right:60px;top:70px;color:#fff;text-align:center}}
.h{{font:800 64px/1.08 'Inter Tight';letter-spacing:-1px}}
.h b{{color:#FFD43B;font-weight:900}}
.o{{display:inline-block;margin-top:34px;background:#E31B23;color:#fff;font:900 84px/1 'Inter Tight';letter-spacing:-2px;padding:22px 34px 20px;border-radius:14px;transform:rotate(-1.5deg);box-shadow:0 10px 30px rgba(0,0,0,.35)}}
.s{{margin-top:30px;font:700 38px/1.2 'Inter';color:#fff}}
"""
body = """<div class="shade"></div><div class="t">
<div class="h">När klockan slår <b>23:59</b><br>är höstrean slut</div>
<div class="o fit">UPP TILL 50 % RABATT</div>
<div class="s">Köp 2 – spara 379 kr · Fri frakt</div></div>"""
ADS = [{"out": "../ut/SE_19_klockan_4x5.png", "w": 1080, "h": 1350, "css": css, "body": body}]
