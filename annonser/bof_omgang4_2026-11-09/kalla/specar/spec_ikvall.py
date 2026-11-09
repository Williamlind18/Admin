import pathlib
W = pathlib.Path(__file__).resolve().parent
BOX = (W / "kartong_frilagd.png").as_uri()
GRA = (W / "kartong_gra.png").as_uri()
css = """
body{background:#fff;font-family:'Inter Tight',sans-serif}
.top{position:absolute;left:0;top:0;width:1080px;height:250px;background:#111;color:#fff;text-align:center;padding-top:44px}
.top .k{font:900 92px/1 'Inter Tight';letter-spacing:-2px}
.top .k span{color:#FFD43B}
.top .s{font:600 34px/1 'Inter';margin-top:22px;color:#ddd;letter-spacing:.2px}
.col{position:absolute;top:250px;height:960px;width:540px;text-align:center}
.l{left:0;background:#E31B23;color:#fff}
.r{left:540px;background:#EDEDED;color:#8a8a8a}
.when{font:900 96px/1 'Inter Tight';letter-spacing:-1px;margin-top:62px}
.r .when{color:#9a9a9a}
.sub{font:700 30px/1 'Inter';margin-top:16px;opacity:.95}
.boxes{position:relative;height:420px;margin-top:40px}
.boxes img{position:absolute;width:250px}
.boxes .b1{left:70px;top:40px;transform:rotate(-5deg)}
.boxes .b2{left:220px;top:70px;transform:rotate(4deg)}
.l .boxes img{filter:drop-shadow(0 18px 22px rgba(0,0,0,.35))}
.r .boxes img{filter:drop-shadow(0 14px 16px rgba(0,0,0,.12))}
.price{font:900 150px/1 'Inter Tight';letter-spacing:-5px;margin-top:20px}
.price small{font-size:70px;letter-spacing:-1px;margin-left:6px}
.r .price{color:#a6a6a6}
.note{font:700 30px/1.25 'Inter';margin-top:18px}
.r .note{color:#9a9a9a;font-weight:600}
.vs{position:absolute;left:480px;top:640px;width:120px;height:120px;border-radius:60px;background:#fff;color:#111;
 font:900 40px/120px 'Inter Tight';text-align:center;box-shadow:0 6px 24px rgba(0,0,0,.25);z-index:3}
.bot{position:absolute;left:0;top:1210px;width:1080px;height:140px;background:#111;color:#fff;text-align:center;
 font:800 44px/140px 'Inter Tight';letter-spacing:-.3px}
.bot span{color:#FFD43B}
"""
body = f"""
<div class="top"><div class="k fit">KÖP 2 – <span>SPARA 379 KR</span></div>
<div class="s">Höstrea · upp till 50 % rabatt · fri frakt</div></div>
<div class="col l"><div class="when">IKVÄLL</div><div class="sub">till 23:59</div>
<div class="boxes"><img class="b1" src="{BOX}"><img class="b2" src="{BOX}"></div>
<div class="price">619<small>kr</small></div><div class="note">2-pack · 24 tabletter</div></div>
<div class="col r"><div class="when">IMORGON</div><div class="sub">&nbsp;</div>
<div class="boxes"><img class="b1" src="{GRA}"><img class="b2" src="{GRA}"></div>
<div class="price">998<small>kr</small></div><div class="note">ordinarie pris</div></div>
<div class="vs">VS</div>
<div class="bot">Höstrean avslutas <span>ikväll 23:59</span></div>
"""
ADS = [{"out": "../ut/SE_18_ikvall_imorgon_4x5.png", "w": 1080, "h": 1350, "css": css, "body": body}]
