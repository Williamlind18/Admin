#!/usr/bin/env python3
"""A1 C5 (video32): turn the Norwegian delivery's labels into Danish.

For each label: find the Norwegian text (by colour) in its region, frame by frame; write a LaMa mask for the text
(text labels) and a PNG sequence with the Danish text in the same colour, size, outline and position, with the
Norwegian label's per-frame opacity (so pop-ins and fades follow). Pills are redrawn instead of inpainted.

usage (from dk2/): a1c5_labels.py            -> work/a1c5_labelmasks.json, ov/a1c5/<name>/%04d.png, ov/a1c5/spec.json
"""
import json
import os
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT = os.path.join(S, "v22it", "fonts", "Montserrat-ExtraBold.ttf")
SRC = "work/a1c5_no.mp4"
W, H, FPS = 720, 900, 30

# name, kind, colour class, search window (s), region, Norwegian text, Danish text, extra
LABELS = [
    dict(name="vanlig1", kind="pill_white", t=(1.0, 6.6), roi=(30, 28, 340, 98), no="VANLIG TABLETT", da="ALMINDELIG TABLET"),
    dict(name="vanlig2", kind="pill_white", t=(27.5, 33.6), roi=(30, 28, 340, 98), no="VANLIG TABLETT", da="ALMINDELIG TABLET"),
    dict(name="vanlig3", kind="pill_white", t=(44.5, 48.6), roi=(190, 262, 530, 338), no="VANLIG TABLETT", da="ALMINDELIG TABLET"),
    dict(name="opfundet", kind="text", col="outlined", t=(35.5, 39.7), roi=(230, 68, 490, 126), no="OPPFUNNET", da="OPFUNDET"),
    dict(name="renser", kind="text", col="red", t=(44.5, 48.6), roi=(230, 64, 490, 114), no="RENSER BARE", da="RENSER KUN"),
    dict(name="dyrehaar", kind="words", col="outlined", t=(48.6, 53.3), roi=(170, 46, 550, 94),
         no=["DYREHÅR", "·", "FLASS", "·", "FETT"], da=["DYREHÅR", "·", "SKÆL", "·", "FEDT"]),
    dict(name="ilt1", kind="text", col="outlined", t=(52.9, 53.97), roi=(185, 385, 545, 437), no="OKSYGENBASERT", da="ILTBASERET", italic=True),
    dict(name="ilt2", kind="text", col="outlined", t=(52.9, 53.97), roi=(215, 450, 515, 500), no="BLEKEMIDDEL", da="BLEGEMIDDEL", italic=True),
    dict(name="dage", kind="text", col="red", t=(96.4, 102.0), roi=(95, 86, 255, 134), no="2 DAGER", da="2 DAGE"),
    dict(name="udsalg", kind="text", col="cyan", t=(101.3, 105.3), roi=(150, 262, 570, 392), no="SALG", da="UDSALG", glow=True),
    dict(name="optil", kind="text", col="outlined", t=(101.3, 105.3), roi=(200, 405, 520, 468), no="OPPTIL 50 %", da="OP TIL 50 %"),
    dict(name="fragt", kind="text", col="outlined", t=(101.3, 105.3), roi=(230, 478, 490, 532), no="+ FRI FRAKT", da="+ FRI FRAGT"),
    dict(name="firepak", kind="text", col="outlined", t=(104.4, 109.7), roi=(190, 42, 530, 88), no="MED FIREPAKNINGEN", da="MED FIREPAKKEN"),
    dict(name="pertab", kind="text", col="outlined", t=(106.4, 109.7), roi=(240, 196, 480, 248), no="PER TABLETT", da="PER TABLET"),
    dict(name="dages", kind="text", col="lightblue", t=(109.4, 115.2), roi=(190, 282, 530, 352), no="30 DAGERS", da="30 DAGES"),
    dict(name="pengene", kind="pill_black", t=(110.8, 115.2), roi=(140, 360, 585, 444), no="PENGENE TILBAKE", da="PENGENE TILBAGE"),
]


def frames(t0, t1):
    i0 = int(round(t0 * FPS))
    pr = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{i0 / FPS:.4f}", "-i", SRC, "-frames:v",
                         str(int(round((t1 - t0) * FPS))), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                        capture_output=True).stdout
    return i0, np.frombuffer(pr, np.uint8).reshape(-1, H, W, 3)


def colour_mask(c, col):
    c = c.astype(int)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    if col == "white":
        return (np.minimum(np.minimum(r, g), b) > 205)
    if col == "outlined":   # light text with a dark rim: light pixels within a few px of very dark ones
        light = (np.minimum(np.minimum(r, g), b) > 190).astype(np.uint8)
        dark = (np.maximum(np.maximum(r, g), b) < 70).astype(np.uint8)
        return (light & cv2.dilate(dark, np.ones((7, 7), np.uint8))).astype(bool)
    if col == "red":
        return (r > 170) & (g < 110) & (b < 120)
    if col == "lightblue":
        return (b > 200) & (g > 170) & (b - r > 40)
    if col == "cyan":
        return (b > 170) & (g > 150) & (r < 160)
    raise ValueError(col)


def text_width(t, size):
    f = ImageFont.truetype(FONT, max(4, int(round(size))))
    l, tt, r, bb = f.getbbox(t)
    return r - l


def render_text(text, size, fill, outline, sw, italic=False, glow=None):
    size, sw = float(size), int(sw)
    fill, outline = [int(v) for v in fill], [int(v) for v in outline]
    glow = [int(v) for v in glow] if glow is not None else None
    f = ImageFont.truetype(FONT, max(4, int(round(size))))
    l, t, r, b = f.getbbox(text, stroke_width=sw)
    pad = int(size * 0.6) + 4
    img = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad - l, pad - t), text, font=f, fill=tuple(fill) + (255,), stroke_width=sw, stroke_fill=tuple(outline) + (255,))
    if glow is not None:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).text((pad - l, pad - t), text, font=f, fill=tuple(glow) + (255,), stroke_width=sw + 2)
        g = g.filter(ImageFilter.GaussianBlur(float(size) * 0.12))
        a = np.array(g); a[..., 3] = (a[..., 3] * 0.9).astype(np.uint8); g = Image.fromarray(a)
        g.alpha_composite(img); img = g
    if italic:
        sh = 0.2
        img = img.transform((img.size[0] + int(img.size[1] * sh), img.size[1]), Image.AFFINE,
                            (1, sh, -img.size[1] * sh, 0, 1, 0), resample=Image.BICUBIC)
    # ink box of the fill (not the glow) for placement
    a = np.array(img)[..., 3]
    ys, xs = np.where(a > 128)
    return img, (xs.min(), ys.min(), xs.max(), ys.max())


def place(canvas, img, ink, cx, bottom):
    x0, y0, x1, y1 = ink
    canvas.alpha_composite(img, (int(round(cx - (x0 + x1) / 2)), int(round(bottom - y1))))


def main():
    os.makedirs("ov/a1c5", exist_ok=True)
    masks, items = {}, []
    for L in LABELS:
        i0, F = frames(*L["t"])
        x0, y0, x1, y1 = L["roi"]
        crops = F[:, y0:y1, x0:x1]
        out = os.path.join("ov/a1c5", L["name"])
        os.makedirs(out, exist_ok=True)
        for fn in os.listdir(out):
            os.remove(os.path.join(out, fn))
        if L["kind"].startswith("pill"):
            dark = L["kind"] == "pill_black"
            g = crops.astype(int).min(3) if not dark else crops.astype(int).max(3)
            pill = (g > 222) if not dark else (g < 45)
            cnt = pill.reshape(len(F), -1).sum(1).astype(float)
        else:
            tm = np.stack([colour_mask(c, L["col"]) for c in crops])
            cnt = tm.reshape(len(F), -1).sum(1).astype(float)
        ref_n = np.percentile(cnt[cnt > 0], 75) if (cnt > 0).any() else 0
        alpha = np.clip(cnt / max(ref_n, 1), 0, 1)
        on = np.where(alpha > 0.06)[0]
        if not len(on):
            print(L["name"], "NOT FOUND"); continue
        ri = on[np.argmin(np.abs(alpha[on] - 1))] if L["kind"] != "words" else on[-1]
        ref = crops[ri]
        if L["kind"].startswith("pill"):
            dark = L["kind"] == "pill_black"
            g = ref.astype(int).min(2) if not dark else ref.astype(int).max(2)
            pill = ((g > 222) if not dark else (g < 45)).astype(np.uint8)
            pill = cv2.morphologyEx(pill, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
            n, lab, st, _ = cv2.connectedComponentsWithStats(pill)
            j = max(range(1, n), key=lambda j: st[j][4])
            px, py, pw, ph = st[j][:4]
            inner = (ref.astype(int).max(2) < 110) if not dark else (ref.astype(int).min(2) > 170)
            # the text = ink components inside the pill that don't touch its edge (the corners show background)
            box = inner[py:py + ph, px:px + pw].astype(np.uint8)
            n2, lab2, st2, _ = cv2.connectedComponentsWithStats(box)
            keep = [q for q in range(1, n2) if st2[q][0] > 2 and st2[q][1] > 2 and st2[q][0] + st2[q][2] < pw - 2
                    and st2[q][1] + st2[q][3] < ph - 2 and st2[q][4] >= 4]
            ys, xs = np.where(np.isin(lab2, keep))
            ys = ys - 3
            tw = xs.max() - xs.min() + 1
            size = L.get("size") or 100 * tw / text_width(L["no"], 100)
            if L.get("size"):
                tw = text_width(L["no"], size)
            f = ImageFont.truetype(FONT, int(round(size)))
            dw = text_width(L["da"], size)
            padx = (pw - tw) / 2
            nw = max(pw, dw + 2 * padx)
            cx, cy = x0 + px + pw / 2, y0 + py + ph / 2
            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            bx0, by0, bx1, by1 = cx - nw / 2 - 1, cy - ph / 2 - 1, cx + nw / 2 + 1, cy + ph / 2 + 1
            d.rounded_rectangle((bx0, by0, bx1, by1), (ph + 2) / 2, fill=(20, 20, 20, 255) if dark else (255, 255, 255, 255))
            l, t, r, b = f.getbbox(L["da"])
            ty = y0 + py + 3 + ys.max() - (b - t)    # same ink bottom as the Norwegian text
            d.text((cx - (l + r) / 2, ty - t), L["da"], font=f, fill=(255, 255, 255, 255) if dark else (0, 0, 0, 255))
            base = np.array(img)
            info = f"pill {pw}x{ph} -> {int(nw)} size {size:.1f}"
        else:
            tmr = colour_mask(ref, L["col"]).astype(np.uint8)
            tmr = cv2.morphologyEx(tmr, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
            ys, xs = np.where(tmr)
            tx0, tx1, ty0, ty1 = xs.min(), xs.max(), ys.min(), ys.max()
            fillc = np.median(ref[tmr > 0], 0).astype(int)
            if L["col"] in ("white", "outlined") and fillc.min() > 170:
                fillc = np.array([255, 255, 255])
            ring = cv2.dilate(tmr, np.ones((7, 7), np.uint8)) - tmr
            dk = ref[ring > 0]; dk = dk[dk.astype(int).sum(1) < 200]
            outl = np.median(dk, 0).astype(int) if len(dk) > 20 else np.array([10, 10, 30])
            canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            if L["kind"] == "words":
                # the Norwegian line is revealed word by word; place the Danish words of the full line the same way
                full_no, full_da = " ".join(L["no"]), " ".join(L["da"])
                size = 100 * (tx1 - tx0) / text_width(full_no, 100)
                sw = max(1, round(size * 0.07))
                cx, bottom = x0 + (tx0 + tx1) / 2, y0 + ty1
                fnt = ImageFont.truetype(FONT, int(round(size)))
                lfull = fnt.getbbox(full_da)
                left = cx - (lfull[2] - lfull[0]) / 2
                word_x, acc = [], ""
                for k, w in enumerate(L["da"]):
                    pre = (acc + " ") if acc else ""
                    word_x.append(left + (fnt.getbbox(pre + w)[2] - fnt.getbbox(w)[2] + fnt.getbbox(w)[0]) - lfull[0])
                    acc = pre + w
                # Norwegian word x-ranges in the reference frame (for the reveal test)
                fnt_no = ImageFont.truetype(FONT, int(round(size)))
                lno = fnt_no.getbbox(full_no); left_no = x0 + tx0
                rngs, acc = [], ""
                for w in L["no"]:
                    pre = (acc + " ") if acc else ""
                    a = left_no + fnt_no.getbbox(pre + w)[2] - fnt_no.getbbox(w)[2] + fnt_no.getbbox(w)[0] - lno[0]
                    rngs.append((a, a + fnt_no.getbbox(w)[2] - fnt_no.getbbox(w)[0]))
                    acc = pre + w
                fdk = ImageFont.truetype(FONT, int(round(size)))
                lead = cx - fdk.getlength(full_da) / 2
                word_pos = [lead + fdk.getlength(" ".join(L["da"][:q]) + (" " if q else "")) for q in range(len(L["da"]))]
                wfill, wout = tuple(int(v) for v in fillc) + (255,), tuple(int(v) for v in outl) + (255,)
                info = f"words size {size:.1f}"
            else:
                size = 100 * (tx1 - tx0) / text_width(L["no"], 100)
                if L.get("italic"):
                    size *= 0.93
                sw = max(1, round(size * 0.07))
                im, ink = render_text(L["da"], size, fillc, outl, sw, italic=L.get("italic", False),
                                      glow=fillc if L.get("glow") else None)
                place(canvas, im, ink, x0 + (tx0 + tx1) / 2, y0 + ty1)
                base = np.array(canvas)
                info = f"size {size:.1f} fill {fillc.tolist()} outline {outl.tolist()}"
        # per-frame output + masks
        first, last = on[0], on[-1]
        for k in range(first, last + 1):
            a = float(alpha[k])
            if L["kind"] == "words":
                canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                m = colour_mask(crops[k], L["col"])
                vis = [m[:, max(0, int(ra - x0)):max(0, int(rb - x0))].sum() > 25 for ra, rb in rngs]
                for q, w in enumerate(L["da"]):        # a separator shows with the word after it
                    if w in "·-|" and q + 1 < len(vis):
                        vis[q] = vis[q + 1]
                dd = ImageDraw.Draw(canvas)
                for q, v in enumerate(vis):
                    if v:
                        dd.text((word_pos[q], y0 + ty1), L["da"][q], font=fdk, fill=wfill, anchor="ls",
                                stroke_width=sw, stroke_fill=wout)
                arr = np.array(canvas)
            else:
                arr = base.copy()
                arr[..., 3] = (arr[..., 3].astype(float) * a).astype(np.uint8)
            Image.fromarray(arr).save(os.path.join(out, f"{k - first:04d}.png"))
            if not L["kind"].startswith("pill") and a > 0.02:
                m = colour_mask(crops[k], L["col"]).astype(np.uint8)
                if m.sum() > 10:
                    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
                    yy, xx = np.where(m)
                    pad = 10 + (int(size * 0.3) if L.get("glow") else 0)
                    r = [int(x0 + xx.min() - pad), int(y0 + yy.min() - pad), int(x0 + xx.max() + pad), int(y0 + yy.max() + pad)]
                    masks.setdefault(i0 + k, []).append(r)
        t0 = (i0 + first) / FPS
        items.append(dict(kind="seq", name=L["name"], pattern=f"{out}/%04d.png", n=int(last - first + 1),
                          t0=round(t0, 3), t1=round((i0 + last + 1) / FPS - 0.01, 3)))
        print(L["name"], f"{t0:.2f}-{(i0 + last + 1) / FPS:.2f}", info)
    json.dump({str(k): v for k, v in sorted(masks.items())}, open("work/a1c5_labelmasks.json", "w"))
    sp = "ov/a1c5/spec.json"
    spec = json.load(open(sp)) if os.path.exists(sp) else dict(items=[])
    names = {L["name"] for L in LABELS}
    spec["items"] = [it for it in spec["items"] if it.get("name") not in names] + items
    json.dump(spec, open(sp, "w"), indent=1)
    print("mask frames", len(masks))


if __name__ == "__main__":
    main()
