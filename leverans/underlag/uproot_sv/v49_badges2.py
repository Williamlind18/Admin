"""Swedish text on video49's two badges (frames 1272-1403): 'Inget slipande' and 'INGET FRÄTANDE' ribbons.
Input patches/v49_badges_raw.mp4 (LaMa removed badge-1 text + captions), output patches/v49_badges.mp4."""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import *
import numpy as np, cv2
from PIL import Image, ImageDraw
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 720, 1280, 30
F0, F1 = 1271, 1403
_o = json.load(open(f'{S}/tmp/v49_badge_off2.json'))
T1 = {int(k): v for k, v in _o['t1'].items()}; RB = {int(k): v for k, v in _o['rb'].items()}
def grad_word(txt, f, top, bot, stroke=3):
    m = text_layer(txt, f, fill=(255, 255, 255, 255), pad=10)
    a = np.asarray(m)[:, :, 3].astype(np.float32) / 255
    h = a.shape[0]
    t = np.linspace(0, 1, h)[:, None, None]
    col = np.array(top)[None, None, :] * (1 - t) + np.array(bot)[None, None, :] * t
    fill = np.dstack([np.broadcast_to(col, a.shape + (3,)), a * 255]).astype(np.uint8)
    st = text_layer(txt, f, fill=(255, 255, 255, 255), stroke=stroke, stroke_fill=(255, 255, 255, 255), pad=10 - stroke + stroke)
    out = Image.new('RGBA', st.size, (0, 0, 0, 0))
    out.alpha_composite(st)
    out.alpha_composite(Image.fromarray(fill), ((st.width - m.width) // 2, (st.height - m.height) // 2))
    return out
def build_b1():
    f = font('mont_i', 40, 800)
    cap = cap_height(f); f = font('mont_i', 40 * 33 / cap, 800)
    w1 = grad_word('Inget', f, (98, 190, 55), (40, 130, 30))
    w2 = grad_word('slipande', f, (40, 140, 225), (20, 80, 170))
    sp = 8
    lay = Image.new('RGBA', (w1.width + w2.width + sp, max(w1.height, w2.height)), (0, 0, 0, 0))
    lay.alpha_composite(w1, (0, 0)); lay.alpha_composite(w2, (w1.width + sp - 6, 0))
    x0, y0, x1, y1 = ink_bbox(lay)
    lay = lay.crop((x0 - 4, y0 - 4, x1 + 4, y1 + 4))
    if lay.width > 330:
        s = 330 / lay.width; lay = lay.resize((330, int(lay.height * s)), Image.LANCZOS)
    sh, m = shadow(lay, radius=3, offset=(1, 2), opacity=0.35)
    fs = font('mont', 13, 600)
    small = text_layer('—  T V Ä T T M A S K I N  —', fs, fill=(45, 75, 120, 150), pad=4)
    return sh, small
B1, SMALL = build_b1()
fr1 = font('mont_xb', 10); fr1 = font('mont_xb', 10 * 23 / cap_height(fr1))
R1 = text_layer('INGET FRÄTANDE', fr1, fill=(28, 96, 34, 255), pad=4).rotate(2.5, resample=Image.BICUBIC, expand=True)
if R1.width > 244: R1 = R1.resize((244, int(R1.height * 244 / R1.width)), Image.LANCZOS)
fr2 = font('mont_xb', 10); fr2 = font('mont_xb', 10 * 15 / cap_height(fr2))
R2 = text_layer('TVÄTTMASKIN', fr2, fill=(255, 255, 255, 255), pad=4).rotate(2.0, resample=Image.BICUBIC, expand=True)
def ribbon_clean(img, dx, dy):
    dx, dy = int(round(dx)), int(round(dy))
    g = img[:, :, 1].astype(np.float32); mn = img.min(2)
    bgG = cv2.medianBlur(img[:, :, 1], 21).astype(np.float32)
    bgM = cv2.medianBlur(mn.astype(np.uint8), 21).astype(np.float32)
    dark = ((bgG - g > 18) & (img[:, :, 1] >= img[:, :, 0])) | ((img[:, :, 1].astype(int) < 165) & (img[:, :, 0].astype(int) < 120))
    white = (mn.astype(np.float32) - bgM > 35) | (mn > 175)
    m = np.zeros((H, W), np.uint8)
    for (x0, y0, x1, y1), sel in (((420, 715, 670, 752), dark), ((450, 753, 642, 777), white)):
        x0, x1, y0, y1 = x0 + dx, x1 + dx, y0 + dy, y1 + dy
        xa, xb = max(0, x0), min(W, x1)
        if xa < xb: m[y0:y1, xa:xb] = sel[y0:y1, xa:xb]
    if not m.any(): return img
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    return cv2.inpaint(img, m * 255, 4, cv2.INPAINT_TELEA)
def put_center(img, lay, cx, cy):
    x0, y0, x1, y1 = ink_bbox(lay)
    composite(img, lay, cx - (x0 + x1) / 2, cy - (y0 + y1) / 2)
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', f'{S}/patches/v49_badges_raw2.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', f'{S}/patches/v49_badges.mp4'], stdin=subprocess.PIPE)
for f in range(F0, F1 + 1):
    img = np.frombuffer(dec.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3).copy()
    if f in RB:
        dx, dy = RB[f]
        img = ribbon_clean(img, dx, dy)
        put_center(img, R1, 545 + dx, 733 + dy)
        put_center(img, R2, 546 + dx, 765 + dy)
    dx, dy = T1[f]
    put_center(img, B1, 545 + dx, 508 + dy)
    put_center(img, SMALL, 540 + dx, 546 + dy)
    enc.stdin.write(img.tobytes())
enc.stdin.close(); enc.wait(); print('ok')
