import pathlib
W = pathlib.Path(__file__).resolve().parent
BG = (W.parent / "bfai" / "svart.png").as_uri()
def tape(text, top, rot, n=6):
    seg = f"<span>{text}</span><i></i>" * n
    return f'<div class="tape" style="top:{top}px;transform:rotate({rot}deg)"><div class="in">{seg}</div></div>'
css = f"""
body{{background:#000 url('{BG}') no-repeat;background-size:1020px 1266px;background-position:30px 40px;overflow:hidden}}
.tape{{position:absolute;left:-200px;width:1480px;height:118px;background:linear-gradient(180deg,#ffe24a 0%,#FFD400 30%,#f4c800 75%,#e2b800 100%);
  box-shadow:0 14px 30px rgba(0,0,0,.55);display:flex;align-items:center;overflow:hidden}}
.tape:before,.tape:after{{content:"";position:absolute;left:0;right:0;height:14px;
  background:repeating-linear-gradient(-45deg,#111 0 14px,transparent 14px 28px)}}
.tape:before{{top:0}} .tape:after{{bottom:0}}
.in{{display:flex;align-items:center;white-space:nowrap;margin-left:-60px}}
.in span{{font:900 62px/1 'Inter Tight';color:#111;letter-spacing:-.5px;padding:0 26px}}
.in i{{display:inline-block;width:18px;height:18px;border-radius:50%;background:#111}}
.vg{{position:absolute;inset:0;background:linear-gradient(90deg,#000 0,rgba(0,0,0,0) 70px,rgba(0,0,0,0) 1010px,#000 1080px),linear-gradient(180deg,rgba(0,0,0,0) 1120px,rgba(0,0,0,.85) 1250px,#000 1300px)}}
.foot{{position:absolute;left:0;right:0;bottom:52px;text-align:center;color:#fff}}
.foot .h{{font:900 72px/1 'Inter Tight';letter-spacing:-2px}}
.foot .h span{{color:#FFD400}}
.foot .s{{margin-top:16px;font:700 36px/1 'Inter';color:#e6e6e6}}
"""
body = (tape("BLACK FRIDAY", 62, -5) + tape("UPP TILL 50 %", 200, 3)
        + """<div class="vg"></div><div class="foot"><div class="h">Köp 2 – <span>spara 379 kr</span></div><div class="s">Fri frakt · avslutas ikväll 23:59</div></div>""")
ADS = [{"out": "../ut_bf/BF_08_avsparrning_4x5.png", "w": 1080, "h": 1350, "css": css, "body": body}]
