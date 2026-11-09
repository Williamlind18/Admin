"""Find the box front in an AI photo (SIFT + RANSAC against the real rectified box front) and paste the real print,
keeping the photo's light (low-frequency per-channel ratio). Usage: paste_face.py in.png out.png [inset] [quad.json]"""
import json, sys
import cv2, numpy as np
from PIL import Image
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import boxlib

def find_quad(img, tex):
    sift = cv2.SIFT_create(8000)
    g1 = cv2.cvtColor(tex.astype(np.uint8), cv2.COLOR_RGB2GRAY); g2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    k1, d1 = sift.detectAndCompute(g1, None); k2, d2 = sift.detectAndCompute(g2, None)
    m = cv2.BFMatcher().knnMatch(d1, d2, k=2)
    good = [a for a, b in m if a.distance < 0.75 * b.distance]
    src = np.float32([k1[a.queryIdx].pt for a in good]); dst = np.float32([k2[a.trainIdx].pt for a in good])
    H, inl = cv2.findHomography(src, dst, cv2.RANSAC, 4.0)
    h, w = tex.shape[:2]
    q = cv2.perspectiveTransform(np.float32([[[0, 0]], [[w, 0]], [[w, h]], [[0, h]]]), H).reshape(4, 2)
    print("matches", len(good), "inliers", int(inl.sum()), "quad", np.round(q, 1).tolist())
    return q

def main():
    inp, out = sys.argv[1], sys.argv[2]
    inset = float(sys.argv[3]) if len(sys.argv) > 3 else 0.012
    img = np.asarray(Image.open(inp).convert("RGB"))
    tex = boxlib.box_texture(sys.argv[4] if len(sys.argv) > 4 and sys.argv[4].endswith('.png') else "../work/box_8.png", 2)
    ex = next((a.split("=")[1] for a in sys.argv if a.startswith("--exclude=")), None)
    search = img.copy()
    if ex:   # hide an already fixed box so SIFT finds the other one
        x0, y0, x1, y1 = map(int, ex.split(","))
        search[y0:y1, x0:x1] = 128
    q = find_quad(search, tex)
    H, W = img.shape[:2]
    ext = next((float(a.split("=")[1]) for a in sys.argv if a.startswith("--top=")), 0.0)
    if ext:   # the AI box is taller than the real one: continue the teal top band upward
        th = tex.shape[0]; n = int(round(ext * th))
        band = np.repeat(tex[20:30].mean(0, keepdims=True), n + 14, 0)
        tex = np.concatenate([band, tex[14:]], 0)
        q = boxlib.quad_from_plane(q, 0, 1, -ext, 1)
    rgb, al = boxlib.warp_to_quad(tex, q, (W, H))
    # inset mask so worn edges / box outline of the photo stay
    qi = boxlib.quad_from_plane(q, inset, 1 - inset, inset, 1 - inset)
    m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [np.int32(np.round(qi * 4))], 1, shift=2)
    if "--keep-dark" in sys.argv:   # dark things in front of the box (bag edge, handles, ribbon) stay
        lum_ai = img.astype(np.float32) @ np.float32([.299, .587, .114]); lum_tx = rgb @ np.float32([.299, .587, .114])
        occ = ((lum_ai < 55) & (lum_tx > 110)).astype(np.uint8)
        occ = cv2.morphologyEx(occ, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(occ, 8)   # only big dark shapes (ribbon, bag), not AI print strokes
        big = np.zeros(n, bool); big[1:] = st[1:, cv2.CC_STAT_AREA] > 6000
        occ = big[lab].astype(np.uint8)
        occ = cv2.dilate(occ, np.ones((5, 5), np.uint8))
        m = m * (1 - occ.astype(np.float32))
    cy = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--clip-y=")), None)
    if cy:   # something in front of the box from this row down (e.g. the bag)
        m[cy:] = 0
    m = cv2.GaussianBlur(m, (0, 0), 1.5) * al
    f = img.astype(np.float32)
    side = np.linalg.norm(q[1] - q[0])
    s = max(10, side / 5)
    # light = photo / real print, measured only where both are white paper (same material), then spread smoothly
    def white(x):
        mx, mn = x.max(2), x.min(2)
        return ((mx - mn) < 0.45 * np.maximum(mx, 1)) & (mx > 45) & ((x[..., 2] - x[..., 0]) < 12)
    texw = (rgb.min(2) > 205) & ((rgb.max(2) - rgb.min(2)) < 25)
    wm = (texw & white(f)).astype(np.float32) * (m > 0.99)
    wm = cv2.erode(wm, np.ones((5, 5), np.uint8))
    r = np.where(wm[..., None] > 0, f / np.maximum(rgb, 1), 0)
    num = cv2.GaussianBlur(r * wm[..., None], (0, 0), s); den = cv2.GaussianBlur(wm, (0, 0), s)[..., None]
    glob = (r * wm[..., None]).sum((0, 1)) / max(wm.sum(), 1)
    ratio = np.where(den > 1e-3, num / np.maximum(den, 1e-6), glob)
    ratio = np.clip(ratio, 0.25, 1.3)
    print("white px", int(wm.sum()), "mean light", np.round(glob, 3))
    lit = rgb * ratio
    o = f * (1 - m[..., None]) + lit * m[..., None]
    if "--teal" in sys.argv:   # AI drew the box's top/side edges in a bluer hue than the real print: shift them to teal
        x0, y0 = q.min(0) - 0.08 * side; x1, y1 = q.max(0) + 0.08 * side
        x0, y0 = int(max(0, x0)), int(max(0, y0)); x1, y1 = int(min(W, x1)), int(min(H, y1))
        roi = np.clip(o[y0:y1, x0:x1], 0, 255).astype(np.uint8)
        hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV_FULL).astype(np.float32)
        hdeg = hsv[..., 0] * 360 / 256
        sel = ((hdeg > 192) & (hdeg < 228) & (hsv[..., 1] > 70)).astype(np.float32)
        sel = cv2.GaussianBlur(sel, (0, 0), 1.0) * (1 - m[y0:y1, x0:x1])
        hsv2 = hsv.copy(); hsv2[..., 0] = 187 * 256 / 360
        rgb2 = cv2.cvtColor(hsv2.astype(np.uint8), cv2.COLOR_HSV2RGB_FULL).astype(np.float32)
        o[y0:y1, x0:x1] = o[y0:y1, x0:x1] * (1 - sel[..., None]) + rgb2 * sel[..., None]
    Image.fromarray(np.clip(o, 0, 255).astype(np.uint8)).save(out)
    json.dump(np.round(q, 2).tolist(), open(out + ".quad.json", "w"))
    print("ok", out)

if __name__ == "__main__":
    main()
