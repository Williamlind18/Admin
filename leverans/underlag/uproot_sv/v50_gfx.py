"""Swedish graphics for video50 on the cleaned picture:
  455-539   OXYGEN BLEACH -> SYRE- / BLEKMEDEL (plate removes the English title; same motion)
  enzyme labels AMYLAS / PROTEAS / LIPAS (LaMa already removed the English ones)
  2370-2437 cyan pills KÖP 2 FÅ 2 GRATIS / + FRI FRAKT (same top-down wipe)
  2773-2838 closing card (our offer image) instead of Uproot's end still
usage: v50_gfx.py CLEAN_IN.mp4 OUT.mp4"""
import sys, os, json, subprocess, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import *
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_in, out_path = sys.argv[1], sys.argv[2]
W, H = 720, 1280
FPS_STR = '2997/125'
N = 2839
# ---------- OXYGEN BLEACH
OX0, OX1 = 455, 539
oxbb = {int(k): v for k, v in json.load(open(f'{S}/tmp/v50_ox_bbox.json')).items()}
def ox_top(f):
    # settled tops: 558 until 487, 344 from 504; in between the measured top of the text core
    if f <= 486: return 558
    if f >= 504: return 344
    b = oxbb.get(f)
    return b[1] if b else 344
def ox_text_layer(word1='SYRE-', word2='BLEKMEDEL', wmax=520, hmax=163):
    k = 2
    f = font('mont_i', 60 * k, 800)
    l1 = text_layer(word1, f, fill=(214, 230, 255, 255), pad=10)
    l2 = text_layer(word2, f, fill=(214, 230, 255, 255), pad=10)
    b1, b2 = ink_bbox(l1), ink_bbox(l2)
    gap = 10 * k
    wl = max(b1[2] - b1[0], b2[2] - b2[0]); hl = (b1[3] - b1[1]) + gap + (b2[3] - b2[1])
    s = min(wmax * k / wl, hmax * k / hl)
    lay = Image.new('RGBA', (int(wl) + 40, int(hl) + 40), (0, 0, 0, 0))
    lay.alpha_composite(l1.crop(b1), (int((lay.width - (b1[2] - b1[0])) / 2), 20))
    lay.alpha_composite(l2.crop(b2), (int((lay.width - (b2[2] - b2[0])) / 2), 20 + (b1[3] - b1[1]) + gap))
    lay = lay.resize((int(lay.width * s / k), int(lay.height * s / k)), Image.LANCZOS)
    g, m = glow(lay, 14, (110, 170, 255), 1.3)
    g2, m2 = glow(lay, 4, (170, 210, 255), 0.9)
    out = Image.new('RGBA', g.size, (0, 0, 0, 0))
    out.alpha_composite(g); out.alpha_composite(g2, (m - m2, m - m2)); out.alpha_composite(lay, (m, m))
    x0, y0, x1, y1 = m + 20 * s / k, m + 20 * s / k, m + 20 * s / k + wl * s / k, m + 20 * s / k + hl * s / k
    return out, (x0, y0, x1, y1)
OXL, OXB = ox_text_layer()
rnd = random.Random(3)
LET = 'ABCDEFGHIJKLMNOPRSTUVXYZÅÄÖ'
def ox_scramble(f):
    w1, w2 = 'SYRE-', 'BLEKMEDEL'
    lock = 462
    if f >= lock: return OXL, OXB
    def scr(w, i0):
        return ''.join(c if (c == '-' or f >= 459 + (i0 + i) * 0.35) else rnd.choice(LET) for i, c in enumerate(w))
    return ox_text_layer(scr(w1, 0), scr(w2, 2))
OXPLATE = None
# ---------- enzyme labels
ENZ = [(1505, 1509, 1553, 1553, 'AMYLAS', 359), (1624, 1627, 1719, 1722, 'PROTEAS', 361), (1749, 1751, 1841, 1841, 'LIPAS', 361)]
def enz_layer(txt):
    k = 2
    f = font('mont', 40 * k, 300)
    f = font('mont', 40 * k * 53 * k / (cap_height(f)), 300) if False else font('mont', 40 * k * (53 * k) / cap_height(f), 300)
    t = text_layer(txt, f, fill=(255, 255, 255, 255), pad=12)
    t = t.resize((t.width // k, t.height // k), Image.LANCZOS)
    sh, m = shadow(t, radius=3, offset=(1, 2), opacity=0.5)
    b = ink_bbox(t)
    return sh, ((b[0] + b[2]) / 2 + m, (b[1] + b[3]) / 2 + m)
ENZL = {e[4]: enz_layer(e[4]) for e in ENZ}
# ---------- cyan pills
pills = {int(k): v for k, v in json.load(open(f'{S}/tmp/video50_pills_cyan.json')).items()}
CYAN = (20, 227, 214)
def pill_layer(txt, cap=28, h=62, padx=22):
    f = font('lib_b', 40); f = font('lib_b', 40 * cap / cap_height(f))
    d = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    bb = d.textbbox((0, 0), txt, font=f); hb = d.textbbox((0, 0), 'H', font=f)
    w = int(bb[2] - bb[0] + 2 * padx)
    im = Image.new('RGBA', (w, h), CYAN + (255,))
    ImageDraw.Draw(im).text((padx - bb[0], (h - (hb[3] - hb[1])) / 2 - hb[1]), txt, font=f, fill=(255, 255, 255, 255))
    return im
PTOP = pill_layer('KÖP 2 FÅ 2 GRATIS'); PBOT = pill_layer('+ FRI FRAKT')
def draw_pill(img, lay, cx, ytop, ylo, yhi):
    """Place pill with its top at ytop (full height 62), visible only between rows ylo..yhi (wipe)."""
    x = int(round(cx - lay.width / 2))
    a = np.asarray(lay).copy()
    rows = np.arange(lay.height)[:, None] + ytop
    a[:, :, 3] = np.where((rows >= ylo) & (rows <= yhi), a[:, :, 3], 0)
    composite(img, Image.fromarray(a), x, ytop)
# ---------- closing card
CARD = Image.open(f'{S}/tmp/endcard_sv.png').convert('RGB')   # 2x
C0, C1 = 2773, 2838
def card_frame(f, prev):
    t = (f - C0) / (C1 - C0)
    z = 1.0 + 0.04 * t
    cw, ch = CARD.width / z, CARD.height / z
    x0, y0 = (CARD.width - cw) / 2, (CARD.height - ch) / 2
    im = np.asarray(CARD.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)).copy()
    if f < C0 + 5:    # quick white flash from the footage into the card, like the original
        a = (f - C0 + 1) / 5
        white = np.full_like(im, 255)
        mix = prev if prev is not None else white
        im = (mix * (1 - a) + im * a).astype(np.uint8)
    return im
# ---------- main loop
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src_in, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', FPS_STR, '-i', '-',
                       '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', out_path], stdin=subprocess.PIPE)
buf = {}
# OXYGEN plate from the cleaned frames themselves (captions already gone)
frames_ox = []
f = 0; last = None
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    img = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    if OX0 <= f <= OX1:
        frames_ox.append((f, img))
        if f == OX1:
            for ff, im in frames_ox:
                top = ox_top(ff)
                if ff >= 456:
                    m = np.zeros((H, W), np.uint8)
                    m[max(0, top - 50):top + 163 + 24, 75:645] = 1
                    if ff <= 459: m[max(0, top - 50):top + 163 + 24, 0:720] = 1
                    small = cv2.resize(im, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
                    ms = cv2.resize(m, (W // 4, H // 4), interpolation=cv2.INTER_NEAREST)
                    fill = cv2.inpaint(small, ms * 255, 9, cv2.INPAINT_TELEA)
                    fill = cv2.GaussianBlur(fill, (0, 0), 6)
                    fill = cv2.resize(fill, (W, H), interpolation=cv2.INTER_CUBIC)
                    mf = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 5)[..., None]
                    im = (fill * mf + im * (1 - mf)).astype(np.uint8)
                    lay, (bx0, by0, bx1, by1) = ox_scramble(ff)
                    cx, cy = 367, top + 81.5
                    dx = {456: -330, 457: -260, 458: -90, 459: -20}.get(ff, 0)
                    if dx:
                        lay = lay.filter(ImageFilter.BoxBlur(0)).transform(lay.size, Image.AFFINE, (1, 0, 0, 0, 1, 0))
                        arr = np.asarray(lay).astype(np.float32)
                        k = abs(dx) // 6 + 1
                        arr = cv2.blur(arr, (k, 1))
                        lay = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
                    composite(im, lay, cx - (bx0 + bx1) / 2 + dx, cy - (by0 + by1) / 2, 1.0 if ff >= 458 else (0.6 if ff == 457 else 0.35))
                enc.stdin.write(im.tobytes())
            frames_ox = []
        f += 1; last = img; continue
    for a0, a1, b0, b1, txt, cx in ENZ:
        if a0 <= f <= b1:
            al = min(1.0, (f - a0 + 1) / (a1 - a0 + 1)) if f < a1 else (1.0 if f <= b0 else max(0.0, 1 - (f - b0) / (b1 - b0 + 1)))
            lay, (ox, oy) = ENZL[txt]
            composite(img, lay, cx - ox, 764.5 - oy, al)
    if f in pills:
        for band, lay, ytop in (('top', PTOP, 238), ('bot', PBOT, 818)):
            r = pills[f].get(band)
            if r: draw_pill(img, lay, 359.5, ytop, r[1] + 5, r[3] - 5)
    if C0 <= f <= C1:
        img = card_frame(f, last)
    enc.stdin.write(img.tobytes())
    last = img; f += 1
enc.stdin.close(); enc.wait(); print('frames', f)
