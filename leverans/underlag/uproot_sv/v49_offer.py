"""Swedish version of video49's offer motion graphic (frames 2813-3010): KÖP 2 / FÅ 2 / GRATIS, FRI FRAKT badge,
30 dagars pengarna tillbaka box. Writes patches/v49_offer.mp4 (frames 2813..3010)."""
import sys, os, json, subprocess, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import *
from assets49 import title_line, box
import numpy as np, cv2
from PIL import Image
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 720, 1280, 30
F0, F1 = 2813, 3010
PRE = 6  # extra frames read before F0 for clean bg reference
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str((F0 - PRE - 0.5) / FPS), '-i', f'{S}/src/video49.mp4', '-frames:v', str(F1 - F0 + 1 + PRE),
                      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
src = {}
for k in range(F1 - F0 + 1 + PRE):
    src[F0 - PRE + k] = np.frombuffer(p.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3).copy()
def gmask(fr):
    f = fr.astype(int)
    m = (f.min(2) > 150) | ((f[:, :, 2] > 150) & (f[:, :, 2] - f[:, :, 0] > 50)) | \
        ((f[:, :, 0] > 150) & (f[:, :, 1] > 110) & (f[:, :, 0] - f[:, :, 2] > 60))
    return cv2.dilate(m.astype(np.uint8), np.ones((13, 13), np.uint8))
def clean(fr, m):
    out = cv2.inpaint(fr, m * 255, 7, cv2.INPAINT_TELEA)
    bl = cv2.GaussianBlur(out, (0, 0), 10)
    mm = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 6)[..., None]
    return (bl * mm + out * (1 - mm)).astype(np.uint8)
# caption pill in the pre-roll frames (y 838-874) is not part of the graphic: mask it out of the reference too
bg = {}
for f in range(F0 - PRE, F1 + 1):
    if 2878 <= f <= 2918: continue
    m = gmask(src[f])
    if f < F0: m[820:890] = 1
    if m.mean() > 0.2: continue
    bg[f] = clean(src[f], m)
def bg_at(f):
    if f in bg: return bg[f].copy()
    a = max(k for k in bg if k < f) if any(k < f for k in bg) else None
    b = min(k for k in bg if k > f) if any(k > f for k in bg) else None
    if 2878 <= f <= 2918: return bg[2919].copy()
    if a is None: return bg[b].copy()
    if b is None: return bg[a].copy()
    t = (f - a) / (b - a)
    return (bg[a] * (1 - t) + bg[b] * t).astype(np.uint8)
# ---- assets (2x, downscaled at draw time)
LINES = {'KÖP 2': (55, 592), 'FÅ 2': (60, 669.5), 'GRATIS': (64, 751.5)}
T = {txt: title_line(txt, cap) for txt, (cap, cy) in LINES.items()}
BADGE = Image.open(f'{S}/tmp/badge49_sv.png')   # placed at (170, 580) in layout 2
BOX = box()
def draw_line(fr, txt, cx, cy, s=1.0, alpha=1.0, clip=None):
    im, (ox, oy), k = T[txt]
    sc = s / k
    lay = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if clip is not None:   # clip = (kind, frac): 'lr' reveal left->right, 'tb' top->bottom
        kind, frac = clip
        a = np.asarray(lay).copy()
        if kind == 'lr':
            x0, _, x1, _ = ink_bbox(lay); edge = x0 + (x1 - x0) * frac
            xs = np.arange(a.shape[1])[None, :]
            a[:, :, 3] = (a[:, :, 3] * np.clip((edge - xs) / 6 + 0.5, 0, 1)).astype(np.uint8)
        else:
            _, y0, _, y1 = ink_bbox(lay); edge = y0 + (y1 - y0) * frac
            ys = np.arange(a.shape[0])[:, None]
            a[:, :, 3] = (a[:, :, 3] * np.clip((edge - ys) / 6 + 0.5, 0, 1)).astype(np.uint8)
        lay = Image.fromarray(a)
    composite(fr, lay, cx - ox * sc, cy - oy * sc, alpha)
def layout(name):
    # returns dict txt -> (cx, cy, scale) and badge (cx, cy, scale)
    if name == 'L1':
        return {t: (362, cy, 1.0) for t, (cap, cy) in LINES.items()}, None
    if name == 'L2':
        s, top = 0.8, 390
    else:
        s, top = 0.625, 317
    first = LINES['KÖP 2'][1] - LINES['KÖP 2'][0] / 2
    d = {t: (362, top + (cy - first) * s, s) for t, (cap, cy) in LINES.items()}
    b = (365, 677.5, 1.0) if name == 'L2' else (362.5, 537.5, 0.759)
    return d, b
def draw_layout(fr, L, B, alpha=1.0):
    for t, (cx, cy, s) in L.items():
        draw_line(fr, t, cx, cy, s, alpha)
    if B:
        cx, cy, s = B
        lay = BADGE.resize((int(BADGE.width * s), int(BADGE.height * s)), Image.LANCZOS) if s != 1 else BADGE
        composite(fr, lay, cx - lay.width / 2, cy - lay.height / 2, alpha)
def lerp_layout(A, B, t):
    (La, Ba), (Lb, Bb) = A, B
    L = {k: tuple(a + (b - a) * t for a, b in zip(La[k], Lb[k])) for k in La}
    Bx = tuple(a + (b - a) * t for a, b in zip(Ba, Bb))
    return L, Bx
rng = random.Random(7)
SPARK = [(rng.uniform(-14, 14), rng.uniform(-38, 38), rng.uniform(1.2, 3.8), rng.random()) for _ in range(70)]
CONF = []
for i in range(16):
    ang = rng.uniform(0, 2 * math.pi)
    CONF.append(dict(x=362 + 140 * math.cos(ang), y=560 + 180 * math.sin(ang), vx=math.cos(ang) * rng.uniform(16, 30),
                     vy=math.sin(ang) * rng.uniform(16, 30) - 4, rot=rng.uniform(0, 180), vr=rng.uniform(-14, 14),
                     w=rng.uniform(6, 9), h=rng.uniform(22, 34)))
def confetti(fr, f):
    n = f - 2932
    if n < 0: return
    for c in CONF:
        x, y, vx, vy, r = c['x'], c['y'], c['vx'], c['vy'], c['rot']
        for _ in range(n):
            x += vx; y += vy; vx *= 0.93; vy = vy * 0.93 + 0.6; r += c['vr']
        a = 1.0 if f < 2996 else max(0, 1 - (f - 2996) / 8)
        piece = Image.new('RGBA', (int(c['w'] * 2) + 4, int(c['h'] * 2) + 4), (0, 0, 0, 0))
        ImageDraw.Draw(piece).rounded_rectangle([2, 2, piece.width - 3, piece.height - 3], 4, fill=(255, 255, 255, 235))
        piece = piece.resize((piece.width // 2, piece.height // 2), Image.LANCZOS).rotate(r, resample=Image.BICUBIC, expand=True)
        composite(fr, piece, x - piece.width / 2, y - piece.height / 2, a)
from PIL import ImageDraw
def sparkles(fr, f, edge_x, cy, fade):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for dx, dy, r, ph in SPARK:
        tw = 0.5 + 0.5 * math.sin(ph * 6.28 + f * 1.7)
        x, y = edge_x + dx + 30 * math.sin(ph * 9 + f * 0.3), cy + dy
        a = int(255 * tw * fade)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 214, 110, a))
    g = lay.filter(ImageFilter.GaussianBlur(3))
    composite(fr, g, 0, 0, 1.0); composite(fr, lay, 0, 0, 1.0)
from PIL import ImageFilter
# transition hull
def hull_mask(fr):
    f = fr.astype(int)
    yel = (f[:, :, 0] > 170) & (f[:, :, 1] > 140) & (f[:, :, 2] < 120)
    dark = (f.max(2) < 170)
    if yel.sum() > 200:
        xs = np.nonzero(yel.any(0))[0]; front = xs.max() + 4
        dark[:, :front] = False
    ys, xs = np.nonzero(dark)
    m = np.zeros((H, W), np.uint8)
    if len(xs) < 50: return m.astype(np.float32)
    pts = np.column_stack([xs, ys]).astype(np.int32)
    hull = cv2.convexHull(pts)
    cv2.fillConvexPoly(m, hull, 1)
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0)
os.makedirs(f'{S}/patches', exist_ok=True)
enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', f'{S}/patches/v49_offer.mp4'], stdin=subprocess.PIPE)
L1, L2, L3 = layout('L1'), layout('L2'), layout('L3')
BX = BOX
def draw_box(fr, f):
    im, (ox, oy), k = BX
    if f < 2943: return
    if f <= 2973:
        t = ease((f - 2943) / 30, 'out')
        s = 0.40 + 0.10 * t; ang = -45 + 40 * t
        cx = 330 + 30 * t; cy = 700 - 95 * math.sin(math.pi * t * 0.9) + 40 * t
    else:
        t = ease((f - 2973) / 15, 'back') if f < 2988 else 1.0
        s = 0.5 + 0.5 * t; ang = -5 * (1 - min(1, t)); cx = 360; cy = 645 + 42 * min(1.2, t)
    sc = s / k
    lay = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if ang: lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    composite(fr, lay, cx - lay.width / 2, cy - lay.height / 2)
for f in range(F0, F1 + 1):
    if 2878 <= f <= 2887:
        out = src[f].copy()
    else:
        out = bg_at(f)
        if f <= 2850:
            # KÖP 2 sparkle reveal
            frac = (f - 2815) / 11
            if frac > 0:
                draw_line(out, 'KÖP 2', 362, LINES['KÖP 2'][1], 1.0, 1.0, ('lr', min(1, frac)) if frac < 1 else None)
            if f <= 2834:
                im, (ox, oy), k = T['KÖP 2']
                width = 200
                edge = 362 - width / 2 + width * min(1, max(0, frac))
                sparkles(out, f, edge, LINES['KÖP 2'][1], 1.0 if f < 2827 else max(0, 1 - (f - 2827) / 7))
            if f >= 2840:
                fr2 = (f - 2840) / 10
                draw_line(out, 'FÅ 2', 362, LINES['FÅ 2'][1], 0.9 + 0.1 * min(1, fr2), 1.0, ('tb', min(1, fr2)) if fr2 < 1 else None)
            if f >= 2847:
                a = 0.25 + 0.2 * (f - 2847)
                draw_line(out, 'GRATIS', 330, 700, 6.5, a)
        elif f <= 2860:
            draw_line(out, 'KÖP 2', 362, LINES['KÖP 2'][1]); draw_line(out, 'FÅ 2', 362, LINES['FÅ 2'][1])
            t = ease((f - 2850) / 10, 'out')
            s = 6.5 + (1 - 6.5) * t
            draw_line(out, 'GRATIS', 330 + 32 * t, 700 + (LINES['GRATIS'][1] - 700) * t, s)
        elif f <= 2877:
            draw_layout(out, *L1)
        elif f <= 2918:
            mine = bg_at(f); draw_layout(mine, *L2)
            hm = hull_mask(src[f])[..., None]
            out = (mine * hm + src[f] * (1 - hm)).round().astype(np.uint8)
        elif f <= 2930:
            draw_layout(out, *L2)
        else:
            t = ease((f - 2930) / 10) if f < 2940 else 1.0
            draw_layout(out, *lerp_layout(L2, L3, t))
            confetti(out, f)
            draw_box(out, f)
    enc.stdin.write(out.tobytes())
enc.stdin.close(); enc.wait()
print('ok', F1 - F0 + 1)
