"""Nya unika BOF-annonser för Norrtvätt Maskinrent. Samma erbjudande överallt: upp till 50 % rabatt,
höstrean slutar söndag 18/10, köp 2 – spara mer, fri frakt, 30 dagars pengarna-tillbaka-garanti."""
import pathlib
HERE = pathlib.Path(__file__).resolve().parent
BOX3D = (HERE / "bilder/kartong_frilagd.png").as_uri()            # riktig kartong, frilagd
HAND = (HERE.parent / "bilder/shop/box_8.png").as_uri()            # riktig produktbild, kartong i handen
RED = "#D7191F"
ADS = []

# ---------------------------------------------------------------- 5. Kvittot (4:5)
def zigzag(w, h, tooth=18, depth=11):
    pts = []
    n = int(w / tooth)
    for i in range(n + 1):
        x = i * w / n
        pts.append(f"{x:.1f}px {0 if i % 2 == 0 else depth}px")
    for i in range(n, -1, -1):
        x = i * w / n
        pts.append(f"{x:.1f}px {h - (0 if i % 2 == 0 else depth)}px")
    return "polygon(" + ",".join(pts) + ")"

RW, RH = 610, 930
rows = [("Maskinrent 2-pack", ""), ("24 tabletter", "998,00"), ("Höstrea", "−379,00"), ("Frakt", "0,00")]
row_html = "".join(f'<div class="r"><span>{a}</span><span>{b}</span></div>' for a, b in rows)
ADS.append({"out": "ut/SE_5_kvitto_4x5.png", "w": 1080, "h": 1350, "css": f"""
body{{background:radial-gradient(ellipse at 50% 40%,#3a3f45 0%,#24282c 70%,#1b1e21 100%)}}
.head{{position:absolute;left:60px;right:60px;top:58px;text-align:center;color:#fff;font-family:'Inter Tight';font-weight:900;
      font-size:92px;letter-spacing:-.02em;line-height:1}}
.head small{{display:block;font-weight:700;font-size:40px;letter-spacing:.01em;color:#ffd84d;margin-top:14px}}
.wrap{{position:absolute;left:150px;top:300px;transform:rotate(-3.2deg);filter:drop-shadow(0 26px 30px rgba(0,0,0,.55))}}
.rc{{width:{RW}px;height:{RH}px;background:#FBFAF5;clip-path:{zigzag(RW, RH)};padding:58px 52px;font-family:'Space Mono';
     color:#222;font-size:25px;line-height:1.55}}
.c{{text-align:center}} .shop{{font-weight:700;font-size:34px;letter-spacing:.18em}} .dash{{border-top:3px dashed #555;margin:16px 0}}
.r{{display:flex;justify-content:space-between}} .tot{{font-weight:700;font-size:32px}} .save{{font-weight:700;font-size:32px;text-align:center;margin:20px 0 6px}}
.bar{{height:70px;margin:22px 36px 6px;background:repeating-linear-gradient(90deg,#222 0 3px,transparent 3px 6px,#222 6px 7px,transparent 7px 12px,#222 12px 16px,transparent 16px 19px)}}
.ring{{position:absolute;left:92px;top:438px;width:420px;height:118px}}
.box{{position:absolute;right:28px;bottom:36px;width:350px;transform:rotate(7deg);filter:drop-shadow(0 24px 26px rgba(0,0,0,.6))}}
""", "body": f"""
<div class="head fit">UPP TILL 50% RABATT<small>Höstrean avslutas ikväll 23:59</small></div>
<div class="wrap"><div class="rc">
 <div class="c shop">NORRTVÄTT</div><div class="c">Höstrea 2026</div><div class="dash"></div>
 {row_html}<div class="dash"></div>
 <div class="r tot"><span>ATT BETALA</span><span>619,00</span></div><div class="dash"></div>
 <div class="save">DU SPARAR 379 KR</div><div class="dash"></div>
 <div class="c">Rean avslutas ikväll 23:59</div><div class="c">30 dagars pengarna-tillbaka</div>
 <div class="bar"></div><div class="c">Tack för ditt köp!</div>
</div>
<svg class="ring" viewBox="0 0 420 118"><path d="M30 64 C 26 18, 380 6, 400 52 C 418 98, 90 116, 34 92 C 8 80, 40 40, 120 30"
 fill="none" stroke="{RED}" stroke-width="7" stroke-linecap="round" opacity=".92"/></svg>
</div>
<img class="box" src="{BOX3D}">
"""})

# ---------------------------------------------------------------- 6. Rabatt-trappan (4:5)
steps = [(1, "−10%", "37 kr/tablett", "#7b8a93"), (2, "−40%", "26 kr/tablett", "#F0A23B"), (3, "−45%", "22 kr/tablett", "#EE6A2C"), (4, "−50%", "21 kr/tablett", RED)]
cols = ""
BW, BH = 158, 186          # one box (3D cut-out is 516x586)
for i, (n, pct, price, col) in enumerate(steps):
    x = 70 + i * 242
    base = 1150
    stack = "".join(f'<img src="{BOX3D}" style="position:absolute;left:{x + (j % 2) * 6}px;top:{base - (j + 1) * (BH - 26)}px;width:{BW}px">'
                    for j in range(n))
    top = base - n * (BH - 26) - 26
    fs = 40 + i * 8
    cols += (stack + f'<div class="pill" style="left:{x + BW / 2}px;top:{top - 30 - fs * 1.4}px;background:{col};font-size:{fs}px">{pct}</div>'
             f'<div class="pr" style="left:{x + BW / 2}px">{price}<small>{n}-pack</small></div>')
ADS.append({"out": "ut/SE_6_trappan_4x5.png", "w": 1080, "h": 1350, "css": """
body{background:linear-gradient(180deg,#0B2E40 0%,#0E3A50 60%,#0B2E40 100%)}
.t{position:absolute;left:60px;right:60px;top:70px;color:#fff;font-family:'Inter Tight';font-weight:900;font-size:104px;line-height:.98;letter-spacing:-.03em}
.t span{color:#3FD3EA}
.s{position:absolute;left:62px;top:300px;color:#cfe9f1;font-family:'Inter Tight';font-weight:700;font-size:36px}
.pill{position:absolute;transform:translateX(-50%);color:#fff;font-family:'Archivo Black';padding:6px 22px;border-radius:999px;white-space:nowrap;
      box-shadow:0 10px 22px rgba(0,0,0,.35)}
img{filter:drop-shadow(0 14px 16px rgba(0,0,0,.45))}
.pr{position:absolute;top:1172px;transform:translateX(-50%);color:#fff;font-family:'Inter Tight';font-weight:800;font-size:31px;text-align:center;white-space:nowrap;line-height:1.05}
.pr small{display:block;font-weight:500;font-size:24px;color:#9fc6d3}
.f{position:absolute;left:0;right:0;bottom:44px;text-align:center;color:#cfe9f1;font-family:'Inter Tight';font-weight:600;font-size:28px}
""", "body": f'<div class="t">Köp fler.<br><span>Spara mer.</span></div><div class="s">Höstrea – upp till 50 % · avslutas ikväll 23:59</div>'
              f'{cols}<div class="f">Fri frakt · 30 dagars pengarna-tillbaka</div>'})

# ---------------------------------------------------------------- 7. Kalendern (1:1)
days = [""] * 3 + [str(d) for d in range(1, 32)]
days += [""] * (35 - len(days))
weeks = [40, 41, 42, 43, 44]
grid = ""
for r in range(5):
    grid += f'<div class="wk">{weeks[r]}</div>'
    for c in range(7):
        d = days[r * 7 + c]
        cls = "d sun" if c == 6 else "d"
        grid += f'<div class="{cls}">{d}</div>'
ADS.append({"out": "ut/SE_7_kalender_1x1.png", "w": 1080, "h": 1080, "css": f"""
body{{background:linear-gradient(160deg,#EDEFF1,#D9DDE1)}}
.cal{{position:absolute;left:70px;top:60px;width:820px;background:#fff;box-shadow:0 22px 40px rgba(0,0,0,.22);transform:rotate(-1.2deg);border-radius:6px;overflow:hidden}}
.ch{{background:{RED};color:#fff;font-family:'Inter Tight';font-weight:900;font-size:64px;letter-spacing:.06em;padding:26px 40px 22px;display:flex;justify-content:space-between;align-items:baseline}}
.ch small{{font-weight:600;font-size:36px;letter-spacing:.02em}}
.g{{display:grid;grid-template-columns:60px repeat(7,1fr);padding:16px 26px 30px;font-family:'Inter Tight'}}
.hd{{font-weight:700;font-size:22px;color:#777;text-align:center;padding:8px 0 10px}}
.wk{{font-size:20px;color:#aaa;text-align:center;padding-top:20px}}
.d{{height:92px;border-top:1px solid #e3e3e3;font-weight:700;font-size:38px;color:#222;text-align:center;padding-top:16px}}
.sun{{color:{RED}}}
.mark{{position:absolute;left:0;top:0;width:1080px;height:1080px;pointer-events:none}}
.note{{position:absolute;left:452px;top:770px;width:560px;font-family:'Permanent Marker';color:{RED};font-size:58px;line-height:1.05;transform:rotate(-4deg)}}
.note small{{display:block;color:#1d1d1d;font-size:40px;margin-top:10px}}
.box{{position:absolute;left:96px;bottom:6px;width:300px;transform:rotate(-6deg);filter:drop-shadow(0 20px 22px rgba(0,0,0,.35))}}
""", "body": f"""
<div class="cal"><div class="ch">OKTOBER<small>2026</small></div><div class="g">
<div></div>{''.join(f'<div class="hd">{d}</div>' for d in ['MÅ','TI','ON','TO','FR','LÖ','SÖ'])}{grid}</div></div>
<svg class="mark" viewBox="0 0 1080 1080">
 <path d="M856 438 C 814 400, 752 414, 748 458 C 744 512, 822 528, 862 496 C 894 468, 878 424, 828 412" fill="none" stroke="{RED}" stroke-width="8" stroke-linecap="round"/>
 <path d="M772 522 C 760 590, 762 660, 722 736" fill="none" stroke="{RED}" stroke-width="7" stroke-linecap="round"/>
 <path d="M722 736 L 748 724 M722 736 L 722 708" fill="none" stroke="{RED}" stroke-width="7" stroke-linecap="round"/>
</svg>
<div class="note">Höstrean slutar!<small>Upp till 50% rabatt</small></div>
<img class="box" src="{BOX3D}">
"""})

# ---------------------------------------------------------------- 8. Stämpeln (1:1)
ADS.append({"out": "ut/SE_8_stampel_1x1.png", "w": 1080, "h": 1080, "css": f"""
body{{background:#CFEBF2}}
.ph{{position:absolute;left:-100px;top:-10px;width:1060px;height:1060px;background:url('{HAND}') center/cover;
     -webkit-mask-image:linear-gradient(90deg,#000 80%,transparent 100%)}}
.st{{position:absolute;left:640px;top:250px;width:420px;height:420px;transform:rotate(-14deg);mix-blend-mode:multiply}}
.strip{{position:absolute;left:0;right:0;bottom:0;height:96px;background:#0B2E40;color:#fff;display:flex;align-items:center;justify-content:center;
        font-family:'Inter Tight';font-weight:700;font-size:34px;letter-spacing:.01em}}
""", "body": f"""
<div class="ph"></div>
<svg class="st" viewBox="0 0 420 420">
 <defs>
  <filter id="grunge"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="n"/>
   <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.2 1.95" result="m"/>
   <feComposite in="SourceGraphic" in2="m" operator="in"/></filter>
  <path id="arc" d="M210 210 m-158 0 a158 158 0 1 1 316 0 a158 158 0 1 1 -316 0"/>
 </defs>
 <g filter="url(#grunge)" fill="{RED}" stroke="{RED}">
  <circle cx="210" cy="210" r="200" fill="none" stroke-width="12"/>
  <circle cx="210" cy="210" r="124" fill="none" stroke-width="5"/>
  <text font-family="Oswald" font-weight="700" font-size="36" letter-spacing="5" stroke="none">
   <textPath href="#arc" startOffset="0">★ HÖSTREA ★ AVSLUTAS IKVÄLL 23:59 </textPath></text>
  <text x="210" y="168" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="34" stroke="none" letter-spacing="2">UPP TILL</text>
  <text x="210" y="252" text-anchor="middle" font-family="Anton" font-size="96" stroke="none">50%</text>
  <text x="210" y="292" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="34" stroke="none" letter-spacing="3">RABATT</text>
 </g>
</svg>
<div class="strip">Fri frakt · 30 dagars pengarna-tillbaka</div>
"""})

# ---------------------------------------------------------------- 9. Kupongen (4:5)
ADS.append({"out": "ut/SE_9_kupong_4x5.png", "w": 1080, "h": 1350, "css": f"""
body{{background:#13AFCB;background-image:radial-gradient(rgba(255,255,255,.16) 2px,transparent 2.5px);background-size:34px 34px}}
.h{{position:absolute;left:60px;right:60px;top:96px;text-align:center;color:#fff;font-family:'Inter Tight';font-weight:900;font-size:96px;line-height:1;letter-spacing:-.02em}}
.h small{{display:block;font-weight:700;font-size:38px;margin-top:18px;color:#E9FBFF}}
.cut{{position:absolute;left:40px;top:388px;width:1000px;height:740px;border:5px dashed rgba(255,255,255,.9);border-radius:34px;transform:rotate(-2deg)}}
.sc{{position:absolute;left:96px;top:360px;width:74px;height:74px;transform:rotate(-2deg)}}
.cp{{position:absolute;left:78px;top:426px;width:924px;height:664px;background:#fff;border-radius:22px;transform:rotate(-2deg);
     box-shadow:0 22px 38px rgba(0,0,0,.25);
     -webkit-mask:radial-gradient(circle 34px at 0 50%,#0000 98%,#000) left/51% 100% no-repeat,radial-gradient(circle 34px at 100% 50%,#0000 98%,#000) right/51% 100% no-repeat}}
.in{{position:absolute;left:62px;top:56px;width:520px;font-family:'Inter Tight';color:#0B2E40}}
.k{{font-weight:800;font-size:30px;letter-spacing:.32em;color:#13AFCB}}
.u{{font-weight:900;font-size:62px;margin-top:22px;line-height:1}}
.p{{font-family:'Archivo Black';font-size:200px;line-height:.95;color:{RED};letter-spacing:-.03em}}
.r{{font-weight:900;font-size:58px;line-height:1}}
.dl{{position:absolute;left:62px;right:62px;top:470px;border-top:4px dashed #c9d3d8}}
.ft{{position:absolute;left:62px;right:62px;top:500px;font-family:'Inter Tight';color:#0B2E40;font-size:31px;line-height:1.35;font-weight:600}}
.ft b{{font-weight:900}}
.box{{position:absolute;left:652px;top:640px;width:370px;transform:rotate(5deg);filter:drop-shadow(0 22px 24px rgba(0,0,0,.35))}}
.f{{position:absolute;left:0;right:0;bottom:56px;text-align:center;color:#fff;font-family:'Inter Tight';font-weight:700;font-size:32px}}
""", "body": f"""
<div class="h">Klipp till!<small>Höstrean avslutas ikväll 23:59</small></div>
<div class="cut"></div>
<svg class="sc" viewBox="0 0 64 64"><g fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round">
 <circle cx="14" cy="16" r="9"/><circle cx="14" cy="48" r="9"/><path d="M21 22 L58 46 M21 42 L58 18"/></g></svg>
<div class="cp"><div class="in"><div class="k">KUPONG</div><div class="u">UPP TILL</div><div class="p">50%</div><div class="r">RABATT</div></div>
 <div class="dl"></div>
 <div class="ft"><b>Gäller till ikväll kl. 23:59</b><br>Ingen kod behövs</div></div>
<img class="box" src="{BOX3D}">
<div class="f">Fri frakt · 30 dagars pengarna-tillbaka</div>
"""})
