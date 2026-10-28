# Replace the English handwriting in the whiteboard animation with Swedish, frame by frame.
# tracks.json (track.py) says where each line is; the original ink in each frame says how much of the
# line the hand has written, so the Swedish text is "written" in step with the hand.
#   pass 1: measure(frame, n) for every animation frame  -> per-item coverage / precision
#   decide(): which frames each item is shown in and how far it is written
#   pass 2: render(frame, n)
import json, re, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '.')
from items import ITEMS as _I, MANUAL
ITEMS = _I + MANUAL

FONT = 'hfonts/Patrick_Hand.ttf'
TR = json.load(open('tracks.json'))
MOT = {int(k): v for k, v in json.load(open('motion.json')).items()}
_fonts = {}


def font(size):
    size = max(6, int(round(size)))
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT, size)
    return _fonts[size]


_hb = font(200).getbbox('H')
CAPR = (_hb[3] - _hb[1]) / 200.0          # cap height / font size of the handwriting font


def ink(f, thr=60):
    return (255 - f.min(axis=2).astype(np.int16)) > thr


def hand_mask(f):
    hsv = cv2.cvtColor(f, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    skin = ((h <= 14) | (h >= 172)) & (s >= 35) & (s <= 175) & (v >= 90)
    skin = cv2.morphologyEx(skin.astype(np.uint8), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    return cv2.dilate(skin, np.ones((7, 7), np.uint8)) > 0


def stroke_px(mask):
    """Typical stroke width of a binary text mask: twice the distance-transform value on the stroke centre."""
    m = mask.astype(np.uint8)
    if m.sum() < 20:
        return 0.0
    dt = cv2.distanceTransform(np.pad(m, 2), cv2.DIST_L2, 3)
    mx = cv2.dilate(dt, np.ones((3, 3), np.uint8))
    ridge = (dt > 0) & (dt >= mx - 1e-6)
    return float(2 * np.median(dt[ridge])) if ridge.any() else 0.0


def ribbon_interior(crop):
    hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
    sat = ((hsv[..., 1] > 110) & (hsv[..., 2] > 60)).astype(np.uint8)
    sat = cv2.morphologyEx(sat, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    from scipy import ndimage
    filled = ndimage.binary_fill_holes(sat).astype(np.uint8)
    return cv2.erode(filled, np.ones((7, 7), np.uint8)) > 0


def render_mask(text, fs, sw=0):
    f = font(fs)
    bb = f.getbbox(text, stroke_width=sw)
    im = Image.new('L', (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4), 0)
    ImageDraw.Draw(im).text((2 - bb[0], 2 - bb[1]), text, font=f, fill=255, stroke_width=sw, stroke_fill=255)
    return np.array(im) > 127


class Item:
    def __init__(self, it, keyframe):
        self.it = it
        self.id = it['id']
        tr = TR[self.id]
        self.tr = {int(k): v for k, v in tr['tr'].items()}
        x0, y0, x1, y1 = [int(round(v)) for v in tr['box']]
        self.w0, self.h0 = x1 - x0, y1 - y0
        bx, by = self.tr[it['n']][0], self.tr[it['n']][1]
        self.off = (x0 - bx, y0 - by)
        crop = keyframe[y0:y1, x0:x1]
        hm = hand_mask(keyframe)[y0:y1, x0:x1]
        self.ribbon = it.get('kind') == 'ribbon'
        if self.ribbon:
            inter = ribbon_interior(crop)
            self.ref = (crop.min(axis=2) > 185) & inter
            self.bg = np.median(crop[inter & ~self.ref], axis=0)
        else:
            self.ref = ink(crop) & ~hm
        self.refdil = cv2.dilate(self.ref.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        strict = ink(crop, 80) & ~hm
        self.color = tuple(int(c) for c in np.median(crop[strict], axis=0)) if strict.sum() > 10 else (40, 40, 40)
        if self.ribbon:
            self.color = (255, 255, 255)
        self.caps = not re.search(r'[a-z]', it['en'])
        if self.ribbon:
            cols = np.where(self.ref.sum(axis=0) > 0)[0]
            rows = np.where(self.ref.sum(axis=1) > 0.18 * self.ref.sum(axis=1).max())[0]
            wt = cols[-1] - cols[0] + 1
            eb = font(40).getbbox(it['en'])
            self.fs0 = 40 * wt / max(1, (eb[2] - eb[0]) * 1.1)
            self.hcap = self.fs0 * CAPR
            self.captop = (rows[0] + rows[-1]) / 2 - self.hcap / 2
            self.stretch = 1.1
        elif self.caps:
            rows = self.ref.sum(axis=1)
            dense = np.where(rows > 0.18 * rows.max())[0] if rows.max() > 0 else []
            self.hcap = float(dense[-1] - dense[0] + 1) if len(dense) > 3 else tr['hcap']
            self.captop = float(dense[0]) if len(dense) > 3 else 0.0
            self.fs0 = self.hcap / CAPR
            self.stretch = 1.1
        if self.ribbon:
            pass
        elif not self.caps:
            # mixed case: match the width of the English line (x-heights differ between fonts)
            eb = font(40).getbbox(it['en'])
            self.fs0 = 40 * self.w0 / max(1, eb[2] - eb[0])
            hb = font(self.fs0).getbbox(it['en'])
            self.fs0 = min(self.fs0, self.fs0 * 1.2 * self.h0 / max(1, hb[3] - hb[1]))
            self.stretch = 1.0
        sb = font(self.fs0).getbbox(it['sv'])
        sw = (sb[2] - sb[0]) * self.stretch
        maxw = it.get('maxw', self.w0 * (1.3 if len(it['sv']) > len(it['en']) else 1.08))
        if sw > maxw:
            self.fs0 *= maxw / sw
        # extra stroke so the Swedish has the weight of the original pen
        orig = stroke_px(self.ref)
        ours = stroke_px(render_mask(it['en'], self.fs0))
        self.sw = int(max(0, round((orig - ours) / 2)))
        self.metrics = {}     # n -> (cov, prec, det)
        self.show = {}        # n -> progress 0..1

    def box(self, n):
        v = self.tr.get(n)
        if v is None:
            return None
        px, py, s, det = v
        return px + self.off[0] * s, py + self.off[1] * s, self.w0 * s, self.h0 * s, s, det

    def maps(self, n, f, hm):
        b = self.box(n)
        if b is None:
            return None
        x0, y0, w, h, s, det = b
        H, W = f.shape[:2]
        X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x0 + w)), int(np.ceil(y0 + h))
        cx0, cy0, cx1, cy1 = max(0, X0), max(0, Y0), min(W, X1), min(H, Y1)
        if cx1 - cx0 < 4 or cy1 - cy0 < 4:
            return None
        rw, rh = X1 - X0, Y1 - Y0
        sl = (slice(cy0 - Y0, cy1 - Y0), slice(cx0 - X0, cx1 - X0))
        refm = cv2.resize(self.ref.astype(np.uint8), (rw, rh), interpolation=cv2.INTER_NEAREST)[sl] > 0
        refd = cv2.resize(self.refdil.astype(np.uint8), (rw, rh), interpolation=cv2.INTER_NEAREST)[sl] > 0
        cur = ink(f[cy0:cy1, cx0:cx1]) & ~hm[cy0:cy1, cx0:cx1]
        return b, (cx0, cy0, cx1, cy1), refm, refd, cur

    def measure(self, n, f, hm):
        if self.ribbon:
            d = self.tr.get(n, [0, 0, 0, 0])[3]
            self.metrics[n] = (1.0 if d else 0.0, 1.0, d)
            return
        m = self.maps(n, f, hm)
        if m is None:
            return
        b, _, refm, refd, cur = m
        nref = max(1, refm.sum())
        if refm.sum() < 0.3 * self.ref.sum():   # mostly outside the frame
            cov = 1.0 if b[5] else 0.0
            self.metrics[n] = (cov, 1.0, b[5])
            return
        prec = (cur & refd).sum() / max(1, cur.sum())
        cov = (cur & cv2.dilate(refm.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)).sum() / nref
        self.metrics[n] = (float(cov), float(prec), int(b[5]))

    def decide(self):
        M = self.metrics
        det = sorted(n for n, v in M.items() if v[2])
        if not det:
            return
        first, last = det[0], det[-1]
        for n in range(first, last + 1):
            if n in M:
                cov, prec, d = M[n]
                if (d and cov > 0.15) or (not d and cov >= 0.5 and prec >= 0.7):
                    self.show[n] = float(np.clip(cov / 0.85, 0, 1)) if not d else max(0.0, min(1.0, cov / 0.85))
        # write-on before the first detection: static camera, ink grows, all ink belongs to this line
        prev = M[first][0]
        for k in range(1, 61):
            n = first - k
            if n not in M:
                break
            cov, prec, d = M[n]
            mv = MOT.get(n + 1, [0, 0, 0])
            if cov < 0.03 or prec < 0.8 or cov > prev + 0.05 or abs(mv[0]) + abs(mv[1]) > 3:
                break
            self.show[n] = float(np.clip(cov / 0.85, 0, 1))
            prev = cov
        # after the last detection: hold while the text is clearly still there
        for k in range(1, 121):
            n = last + k
            if n not in M:
                break
            cov, prec, d = M[n]
            if cov < 0.6 or prec < 0.8:
                break
            self.show[n] = 1.0


def text_layer(sv, fs, sw, stretch):
    f = font(fs)
    bb = f.getbbox(sv, stroke_width=sw)
    w, h = bb[2] - bb[0] + 4, bb[3] - bb[1] + 4
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).text((2 - bb[0], 2 - bb[1]), sv, font=f, fill=255, stroke_width=sw, stroke_fill=255)
    if stretch != 1.0:
        im = im.resize((int(round(w * stretch)), h), Image.LANCZOS)
    # y offset of the cap line inside the layer, to align caps with the original line
    capy = 2 - bb[1] + (f.getbbox('H')[1])
    return np.array(im).astype(np.float32) / 255.0, capy


def render(f, n, items):
    live = [I for I in items if n in I.show]
    if not live:
        return f
    hm = hand_mask(f)
    H, W = f.shape[:2]
    # drop held items that overlap a detected one (e.g. a new line written where an old one was)
    boxes = {I.id: I.box(n) for I in live}
    keep = []
    for I in live:
        b = boxes[I.id]
        if not b[5]:
            clash = False
            for J in live:
                if J is I or not boxes[J.id][5]:
                    continue
                c = boxes[J.id]
                ix = max(0, min(b[0] + b[2], c[0] + c[2]) - max(b[0], c[0]))
                iy = max(0, min(b[1] + b[3], c[1] + c[3]) - max(b[1], c[1]))
                if ix * iy > 0.3 * min(b[2] * b[3], c[2] * c[3]):
                    clash = True
            if clash:
                continue
        keep.append(I)
    out = f.copy()
    erase = np.zeros((H, W), np.uint8)
    draws = []
    for I in keep:
        m = I.maps(n, f, hm)
        if m is None:
            continue
        (x0, y0, w, h, s, det), (cx0, cy0, cx1, cy1), refm, refd, cur = m
        crop = f[cy0:cy1, cx0:cx1]
        if I.ribbon:
            er = (crop.min(axis=2) > 150) & ribbon_interior(crop)
            color = np.array([255.0, 255.0, 255.0])
            erase[cy0:cy1, cx0:cx1] |= cv2.dilate(er.astype(np.uint8), np.ones((5, 5), np.uint8))
            draws.append((I, x0, y0, w, h, s, color))
            continue
        strict = ink(crop, 80) & refd & ~hm[cy0:cy1, cx0:cx1]
        color = np.median(crop[strict], axis=0) if strict.sum() > 15 else np.array(I.color, float)
        er = refd & ink(crop, 20) & ~hm[cy0:cy1, cx0:cx1]
        erase[cy0:cy1, cx0:cx1] |= er.astype(np.uint8)
        draws.append((I, x0, y0, w, h, s, color))
    erase = cv2.dilate(erase, np.ones((3, 3), np.uint8))
    erase[hm] = 0
    if erase.any():
        ys, xs = np.where(erase > 0)
        ry0, ry1, rx0, rx1 = max(0, ys.min() - 8), min(H, ys.max() + 9), max(0, xs.min() - 8), min(W, xs.max() + 9)
        out[ry0:ry1, rx0:rx1] = cv2.inpaint(out[ry0:ry1, rx0:rx1], erase[ry0:ry1, rx0:rx1], 3, cv2.INPAINT_TELEA)
    for I, x0, y0, w, h, s, color in draws:
        prog = I.show[n]
        fs = I.fs0 * s
        L, capy = text_layer(I.it['sv'], fs, int(round(I.sw * s)), I.stretch)
        th, tw = L.shape
        if I.caps:
            ty = y0 + I.captop * s - capy   # put the cap line where the original capitals start
        else:
            ty = y0 + h / 2 - th / 2 + I.it.get('dy', 0)
        tx = x0 + w / 2 - tw / 2 if I.it['align'] == 'c' else x0 - 2
        if prog < 1:
            ramp = np.clip((prog * tw - np.arange(tw)) / 4.0 + 0.5, 0, 1)
            L = L * ramp[None, :]
        TX, TY = int(round(tx)), int(round(ty))
        lx0, ly0, lx1, ly1 = max(0, TX), max(0, TY), min(W, TX + tw), min(H, TY + th)
        if lx1 <= lx0 or ly1 <= ly0:
            continue
        a = (L[ly0 - TY:ly1 - TY, lx0 - TX:lx1 - TX] * (~hm[ly0:ly1, lx0:lx1]))[..., None]
        dst = out[ly0:ly1, lx0:lx1].astype(np.float32)
        out[ly0:ly1, lx0:lx1] = (dst * (1 - a) + color[None, None, :] * a).clip(0, 255).astype(np.uint8)
    return out
