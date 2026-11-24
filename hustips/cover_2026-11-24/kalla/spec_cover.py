import pathlib
D = pathlib.Path(__file__).resolve().parent
W, H = 1640, 856
HOUSE = ('<svg viewBox="0 0 64 56" width="64" height="56" fill="none" stroke="currentColor" stroke-width="3.2" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M6 27 L32 6 L58 27"/><path d="M13 22 V50 H51 V22"/>'
         '<path d="M27 50 V36 H37 V50"/><path d="M44 12 V18"/></svg>')

def ad(name, bg, pos, top, ink, sub, glow, hsize=168, psize=28, cx=820):
    css = f"""
    body{{background:url('{(D/bg).as_uri()}') {pos}/cover no-repeat}}
    .glow{{position:absolute;left:{cx}px;top:{top}px;width:1100px;height:420px;transform:translate(-50%,-50%);
      background:radial-gradient(ellipse at center,{glow} 0%,rgba(255,255,255,0) 68%)}}
    .t{{position:absolute;left:{cx-500}px;width:1000px;top:{top}px;transform:translateY(-50%);text-align:center;color:{ink}}}
    .ic{{display:block;margin:0 auto 6px;color:{ink};opacity:.85}}
    h1{{font-family:'EB Garamond';font-weight:500;font-size:{hsize}px;line-height:1;letter-spacing:1px}}
    .rule{{width:90px;height:2px;background:{ink};opacity:.55;margin:22px auto 20px}}
    p{{font-family:'Inter';font-weight:400;font-size:{psize}px;letter-spacing:.6px;color:{sub}}}
    """
    body = (f'<div class="glow"></div><div class="t"><span class="ic">{HOUSE}</span><h1>Hustips</h1>'
            '<div class="rule"></div><p>Tips och knep för hemmet. Vi hjälper varandra i vardagen.</p></div>')
    return {"out": f"ut/{name}.png", "w": W, "h": H, "css": css, "body": body}

def plain(name, bg, pos):
    return {"out": f"ut/{name}.png", "w": W, "h": H,
            "css": f"body{{background:url('{(D/bg).as_uri()}') {pos}/cover no-repeat}}", "body": ""}

ADS = [
    ad("hustips_cover_1_koksbank", "bg0.png", "center 40%", 315, "#2e2924", "#4a423a", "rgba(250,246,238,.75)"),
    ad("hustips_cover_2_flatlay", "bg1.png", "center", 428, "#2b241d", "#3d342b", "rgba(250,244,232,.80)"),
    ad("hustips_cover_3_tvattstuga", "bg2b.png", "center 30%", 228, "#26332b", "#33443a", "rgba(236,243,236,.72)", hsize=138, psize=23, cx=1005),
    plain("hustips_cover_1_koksbank_utan_text", "bg0.png", "center 40%"),
    plain("hustips_cover_2_flatlay_utan_text", "bg1.png", "center"),
    plain("hustips_cover_3_tvattstuga_utan_text", "bg2b.png", "center 30%"),
]
