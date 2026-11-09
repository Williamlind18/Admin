"""Black Friday BOF, grafiska annonser. Erbjudande: upp till 50 % rabatt, köp 2 – spara 379 kr (2-pack 619 kr, ord. 998 kr),
fri frakt, 30 dagars pengarna-tillbaka, Black Friday avslutas ikväll 23:59. Inga datum, inget 999 kr, ingen 'höstrea'."""
import pathlib, random
HERE = pathlib.Path(__file__).resolve().parent
BOX = (HERE / "kartong_frilagd.png").as_uri()
GRA = (HERE / "kartong_gra.png").as_uri()
TAB = (HERE / "tablet.png").as_uri()
RED, YEL, TEAL = "#E31B23", "#FFD43B", "#2FD4EC"
ADS = []

def zigzag(w, h, tooth=18, depth=11):
    n = int(w / tooth); pts = []
    for i in range(n + 1): pts.append(f"{i * w / n:.1f}px {0 if i % 2 == 0 else depth}px")
    for i in range(n, -1, -1): pts.append(f"{i * w / n:.1f}px {h - (0 if i % 2 == 0 else depth)}px")
    return "polygon(" + ",".join(pts) + ")"

# ------------------------------------------------ BF_01 Kvittot (iteration av vinnaren C6/B5)
RW, RH = 600, 940
rows = [("Maskinrent 2-pack", ""), ("24 tabletter", "998,00"), ("Black Friday", "−379,00"), ("Frakt", "0,00")]
rh = "".join(f'<div class="r"><span>{a}</span><span>{b}</span></div>' for a, b in rows)
ADS.append({"out": "../ut_bf/BF_01_kvittot_4x5.png", "w": 1080, "h": 1350, "css": f"""
body{{background:radial-gradient(ellipse at 50% 38%,#1d1d1f 0%,#0b0b0c 70%,#050505 100%)}}
.head{{position:absolute;left:50px;right:50px;top:52px;text-align:center;color:#fff;font:900 128px/1 'Inter Tight';letter-spacing:-4px}}
.sub{{position:absolute;left:0;right:0;top:200px;text-align:center;font:800 44px/1 'Inter Tight';color:{YEL}}}
.wrap{{position:absolute;left:330px;top:300px;transform:rotate(1.6deg);filter:drop-shadow(0 26px 34px rgba(0,0,0,.8))}}
.rc{{width:{RW}px;height:{RH}px;background:#FBFAF5;clip-path:{zigzag(RW, RH)};padding:56px 50px;font-family:'Space Mono';color:#1c1c1c;font-size:25px;line-height:1.55}}
.c{{text-align:center}} .shop{{font-weight:700;font-size:34px;letter-spacing:.18em}} .bfh{{display:inline-block;background:#111;color:#fff;font-weight:700;padding:2px 14px;margin-top:6px}}
.dash{{border-top:3px dashed #555;margin:16px 0}} .r{{display:flex;justify-content:space-between}}
.tot{{font-weight:700;font-size:32px}} .save{{position:relative;font-weight:700;font-size:34px;text-align:center;margin:26px 0 12px}}
.bar{{height:70px;margin:22px 36px 6px;background:repeating-linear-gradient(90deg,#222 0 3px,transparent 3px 6px,#222 6px 7px,transparent 7px 12px,#222 12px 16px,transparent 16px 19px)}}
.ring{{position:absolute;left:-14px;top:-40px;width:528px;height:126px}}
.box{{position:absolute;left:34px;bottom:46px;width:360px;transform:rotate(-7deg);filter:drop-shadow(0 24px 30px rgba(0,0,0,.85))}}
""", "body": f"""
<div class="head fit">BLACK FRIDAY</div><div class="sub">Upp till 50 % rabatt · avslutas ikväll 23:59</div>
<div class="wrap"><div class="rc">
 <div class="c shop">NORRTVÄTT</div><div class="c"><span class="bfh">BLACK FRIDAY</span></div><div class="dash"></div>
 {rh}<div class="dash"></div>
 <div class="r tot"><span>ATT BETALA</span><span>619,00</span></div><div class="dash"></div>
 <div class="save">DU SPARAR 379 KR<svg class="ring" viewBox="0 0 528 126"><path d="M40 64 C 36 14, 490 4, 512 54 C 530 104, 100 124, 34 98 C 8 86, 26 36, 140 24" fill="none" stroke="{RED}" stroke-width="7" stroke-linecap="round" opacity=".92"/></svg></div><div class="dash"></div>
 <div class="c">Black Friday avslutas</div><div class="c">ikväll 23:59</div><div class="c">30 dagars pengarna-tillbaka</div>
 <div class="bar"></div><div class="c">Tack för ditt köp!</div>
</div>
</div>
<img class="box" src="{BOX}">"""})

# ------------------------------------------------ BF_03 Från 21 kr/tablett (iteration av C3-ny)
random.seed(4)
floaters = ""
for x, y, w, rot, blur, op in [(-90, -60, 300, 25, 9, .55), (830, 150, 230, -35, 7, .5), (870, 1180, 300, 40, 10, .5), (-60, 1080, 200, -20, 6, .45)]:
    floaters += f'<img src="{TAB}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg);filter:blur({blur}px);opacity:{op}">'
ADS.append({"out": "../ut_bf/BF_03_21kr_tablett_4x5.png", "w": 1080, "h": 1350, "css": f"""
body{{background:radial-gradient(ellipse at 50% 55%,#13262b 0%,#081114 55%,#020405 100%);overflow:hidden}}
.pill{{position:absolute;left:50%;top:70px;transform:translateX(-50%) rotate(-2deg);background:{RED};color:#fff;font:900 64px/1 'Inter Tight';letter-spacing:1px;
  padding:18px 40px 16px;border-radius:22px;white-space:nowrap;box-shadow:0 12px 30px rgba(0,0,0,.5)}}
.f{{position:absolute;left:0;right:0;top:196px;text-align:center;font:400 72px/1 'Anton';color:#fff}}
.k{{position:absolute;left:30px;right:30px;top:268px;text-align:center;font:400 178px/1 'Anton';color:#fff}}
.k span{{color:{TEAL}}}
.s{{position:absolute;left:0;right:0;top:470px;text-align:center;font:700 38px/1 'Inter';color:#d5eef3}}
.hero{{position:absolute;left:30px;top:540px;width:400px;filter:drop-shadow(0 0 40px rgba(47,212,236,.45))}}
.b1{{position:absolute;left:430px;top:560px;width:610px;transform:rotate(-7deg);filter:drop-shadow(0 30px 40px rgba(0,0,0,.8))}}
.b2{{position:absolute;left:-30px;top:880px;width:400px;transform:rotate(11deg);filter:drop-shadow(0 30px 40px rgba(0,0,0,.8))}}
.ff{{position:absolute;left:300px;top:900px;width:240px;height:240px;border-radius:50%;background:{RED};color:#fff;text-align:center;
  font:900 62px/.95 'Inter Tight';padding-top:48px;transform:rotate(-8deg);box-shadow:0 14px 34px rgba(0,0,0,.55);z-index:5}}
.ff small{{display:block;font-size:42px}}
.dl{{position:absolute;left:0;right:0;bottom:0;height:120px;background:#000;text-align:center;font:800 44px/120px 'Inter Tight';color:#fff;z-index:6}}
.dl b{{color:{YEL}}}
""", "body": f"""{floaters}
<div class="pill">BLACK FRIDAY</div>
<div class="f">FRÅN</div>
<div class="k fit"><span>21 KR</span>/TABLETT</div>
<div class="s">Upp till 50 % rabatt – sista chansen</div>
<img class="hero" src="{TAB}">
<img class="b1" src="{BOX}"><img class="b2" src="{BOX}">
<div class="ff"><small>+</small>FRI<br>FRAKT</div>
<div class="dl">Black Friday avslutas <b>ikväll 23:59</b></div>"""})

# ------------------------------------------------ BF_04 BLACK / kartong / FRIDAY (iteration av hejdå C8/B4)
ADS.append({"out": "../ut_bf/BF_04_black_friday_4x5.png", "w": 1080, "h": 1350, "css": f"""
body{{background:radial-gradient(ellipse at 50% 50%,#222 0%,#0c0c0c 60%,#000 100%)}}
.top{{position:absolute;left:0;right:0;top:62px;text-align:center;font:800 40px/1 'Inter';letter-spacing:12px;color:{YEL}}}
.w{{position:absolute;left:0;right:0;text-align:center;color:#fff;font:900 250px/1 'Inter Tight';letter-spacing:-8px}}
.w1{{top:120px}} .w2{{top:900px}}
.box{{position:absolute;left:300px;top:345px;width:480px;filter:drop-shadow(0 30px 40px rgba(0,0,0,.9));z-index:2}}
.st{{position:absolute;left:690px;top:330px;width:250px;height:250px;border-radius:50%;background:{RED};color:#fff;text-align:center;z-index:3;
  transform:rotate(12deg);box-shadow:0 12px 30px rgba(0,0,0,.6);font:800 34px/1 'Inter Tight';padding-top:46px}}
.st b{{display:block;font:900 92px/1 'Inter Tight';letter-spacing:-3px;margin:4px 0 2px}}
.dl{{position:absolute;left:0;right:0;top:1180px;text-align:center;font:800 50px/1.2 'Inter Tight';color:#fff}}
.dl b{{color:{YEL}}}
""", "body": f"""<div class="top">SISTA KVÄLLEN</div>
<div class="w w1">BLACK</div><img class="box" src="{BOX}">
<div class="st">UPP TILL<b>50 %</b>RABATT</div>
<div class="w w2">FRIDAY</div>
<div class="dl">Avslutas <b>ikväll 23:59</b></div>"""})

# ------------------------------------------------ BF_10 En vanlig fredag vs Black Friday
ADS.append({"out": "../ut_bf/BF_10_vanlig_fredag_4x5.png", "w": 1080, "h": 1350, "css": f"""
body{{background:#000}}
.a{{position:absolute;left:0;top:0;width:1080px;height:560px;background:#F2F2F0}}
.b{{position:absolute;left:0;top:560px;width:1080px;height:790px;background:#050505}}
.lab{{position:absolute;left:70px;font:800 46px/1 'Inter';letter-spacing:.3px}}
.la{{top:90px;color:#8a8a8a}} .lb{{top:640px;color:{YEL}}}
.p{{position:absolute;left:62px;font:900 230px/1 'Inter Tight';letter-spacing:-9px}}
.pa{{top:170px;color:#b5b5b5}} .pb{{top:720px;color:#fff}}
.p small{{font-size:96px;letter-spacing:-2px;margin-left:10px}}
.pa .x{{position:absolute;left:-10px;right:-10px;top:52%;height:16px;background:{RED};transform:rotate(-6deg);border-radius:8px}}
.na{{position:absolute;left:70px;top:430px;font:600 36px/1.2 'Inter';color:#8a8a8a}}
.nb{{position:absolute;left:70px;top:975px;font:800 52px/1.15 'Inter Tight';color:#fff}}
.nb b{{color:{YEL}}}
.dl{{position:absolute;left:70px;top:1130px;display:inline-block;background:{RED};color:#fff;font:800 42px/1 'Inter Tight';padding:22px 30px;border-radius:14px}}
.bx1{{position:absolute;left:620px;top:360px;width:370px;transform:rotate(6deg);filter:drop-shadow(0 26px 30px rgba(0,0,0,.55))}}
.bx2{{position:absolute;left:740px;top:560px;width:330px;transform:rotate(-5deg);filter:drop-shadow(0 26px 30px rgba(0,0,0,.6))}}
.gr1{{position:absolute;left:690px;top:95px;width:200px;transform:rotate(-4deg);opacity:.95}}
.gr2{{position:absolute;left:840px;top:130px;width:180px;transform:rotate(5deg);opacity:.95}}
""", "body": f"""<div class="a"></div><div class="b"></div>
<div class="lab la">En vanlig fredag</div>
<div class="p pa">998<small>kr</small><span class="x"></span></div>
<div class="na">2-pack Maskinrent</div>
<div class="lab lb">BLACK FRIDAY</div>
<div class="p pb">619<small>kr</small></div>
<div class="nb">Köp 2 – <b>spara 379 kr</b><br>+ fri frakt</div>
<div class="dl">Avslutas ikväll 23:59</div>
<img class="bx1" src="{BOX}"><img class="bx2" src="{BOX}">"""})
