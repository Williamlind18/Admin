"""Danish title and offer text for DK batch 2 C7 (video39), drawn where the Swedish text was (Montserrat Bold, white,
soft dark drop shadow), with each Swedish line's per-frame opacity measured from Swedish vs clean.
usage: c7_overlays_da.py SV.mp4 CLEAN.mp4 OUTDIR   -> OUTDIR/title_%05d.png (frames 0-158), offer_%05d.png (2812-2939)"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SV, CL, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
VF = '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/fonts_dl/Montserrat[wght].ttf'
W, H = 1080, 1920
# Swedish line: (text, fitted size, Swedish ink top, Danish text, group)
L = {'t1': ('En enzymtablett.', 38, 468, 'Én enzymtablet.', 't'),
     't2': ('Det här kom ut ur en', 38, 525, 'Det her kom ud af en', 't'),
     't3': ('”ren” tvättmaskin.', 39, 582, '"ren" vaskemaskine.', 't'),
     'o1': ('KÖP 2', 92, 800, 'KØB 2', 'o'),
     'o2': ('FÅ 2 GRATIS', 93, 901, 'FÅ 2 GRATIS', 'o'),
     'o3': ('Fri frakt + 30 dagars', 48, 1051, 'Fri fragt + 30 dages', 'o'),
     'o4': ('pengarna-tillbaka-garanti', 48, 1131, 'pengene-tilbage-garanti', 'o')}
RNG = {'t': (0, 159), 'o': (2812, 2940)}
def font(s):
    f = ImageFont.truetype(VF, s); f.set_variation_by_axes([700]); return f
def baseline(txt, s, top):
    """baseline that puts txt's ink top at `top`"""
    im = Image.new('L', (1400, 400), 0); ImageDraw.Draw(im).text((20, 200), txt, font=font(s), fill=255, anchor='ls')
    ys = np.where(np.array(im) > 128)[0]; return top + (200 - ys.min())
def frames(p, a, b):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a / 30:.4f}', '-i', p, '-frames:v', str(b - a), '-fps_mode', 'passthrough',
                        '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, H, W).astype(np.float32)
# per-line opacity: on the Swedish line's own ink (as fully shown), alpha = (sv - clean) / (255 - clean)
alpha = {}
for g, (a, b) in RNG.items():
    S, C = frames(SV, a, b), frames(CL, a, b)
    for k, (sv_txt, s, top, da, gg) in L.items():
        if gg != g: continue
        bl = baseline(sv_txt, s, top)
        im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).text((540, bl), sv_txt, font=font(s), fill=255, anchor='ms')
        ink = np.array(im.filter(ImageFilter.MinFilter(3))) > 200
        den = np.maximum(255 - C[:, ink], 30)
        al = np.clip(np.median((S[:, ink] - C[:, ink]) / den, axis=1), 0, 1)
        al[al < 0.06] = 0
        alpha[k] = al.round(3).tolist()
json.dump(alpha, open(os.path.join(OUT, 'alpha.json'), 'w'))
for g, (a, b) in RNG.items():
    keys = [k for k in L if L[k][4] == g]
    for i, f in enumerate(range(a, b)):
        canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for k in keys:
            al = alpha[k][i]
            if al <= 0: continue
            sv_txt, s, top, da, _ = L[k]
            bl = baseline(sv_txt, s, top)
            txt = Image.new('L', (W, H), 0); ImageDraw.Draw(txt).text((540, bl), da, font=font(s), fill=255, anchor='ms')
            off, rad = (2, 3, 3) if s < 60 else (3, 5, 5), None
            sh = Image.new('L', (W, H), 0); sh.paste(txt, off[:2]); sh = sh.filter(ImageFilter.GaussianBlur(off[2]))
            layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            layer.putalpha(sh.point(lambda v: int(v * 0.6 * al)))
            white = Image.new('RGBA', (W, H), (255, 255, 255, 0)); white.putalpha(txt.point(lambda v: int(v * al)))
            canvas = Image.alpha_composite(canvas, layer)
            if s < 60:   # the Swedish title has a dark 2 px outline round the letters as well as the shadow
                st = Image.new('L', (W, H), 0)
                ImageDraw.Draw(st).text((540, bl), da, font=font(s), fill=255, anchor='ms', stroke_width=2, stroke_fill=255)
                rim = Image.new('RGBA', (W, H), (20, 20, 20, 0)); rim.putalpha(st.point(lambda v: int(v * 0.85 * al)))
                canvas = Image.alpha_composite(canvas, rim)
            canvas = Image.alpha_composite(canvas, white)
        canvas.save(os.path.join(OUT, f"{'title' if g == 't' else 'offer'}_{f:05d}.png"), compress_level=1)
print({k: (sum(1 for x in v if x > 0), max(v)) for k, v in alpha.items()})
