#!/usr/bin/env python3
"""Find caption pills (white rounded boxes with black text) in every frame and write LaMa masks.
usage: pilldetect.py SRC OUT.json [--band y0,y1] [--extra json]   (band as fractions of height)"""
import sys, json, subprocess
import numpy as np, cv2
def pills(img, y0, y1):
    H, W = img.shape[:2]
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    white = ((g > 215) & (hsv[:, :, 1] < 35)).astype(np.uint8)
    dark = (g < 90).astype(np.uint8)
    # pill = white region; text holes inside -> close them
    m = cv2.morphologyEx(white, cv2.MORPH_CLOSE, np.ones((9, 15), np.uint8))
    m[:y0] = 0; m[y1:] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    out = []
    for j in range(1, n):
        x, y, w, h, a = st[j]
        if not (16 <= h <= 160 and 30 <= w <= W - 4): continue
        if a < 0.62 * w * h: continue                      # box-like
        inner = dark[y + 4:y + h - 4, x + 4:x + w - 4]
        if inner.size == 0: continue
        d = inner.mean()
        if not (0.03 < d < 0.5): continue                 # holds text
        # rows of text: dark pixels must sit away from the box edge (a real pill has white padding)
        if dark[y:y + 3, x:x + w].mean() > 0.08 or dark[y + h - 3:y + h, x:x + w].mean() > 0.08: continue
        out.append([int(max(0, x - 8)), int(max(0, y - 8)), int(min(W, x + w + 8)), int(min(H, y + h + 8))])
    return out
if __name__ == "__main__":
    src, outp = sys.argv[1], sys.argv[2]
    band = (0.0, 1.0)
    if "--band" in sys.argv: band = tuple(float(v) for v in sys.argv[sys.argv.index("--band") + 1].split(","))
    o = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                   "-of", "json", src], capture_output=True, text=True).stdout)["streams"][0]
    W, H = o["width"], o["height"]
    pr = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    res, i = {}, 0
    while True:
        b = pr.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        img = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        r = pills(img, int(band[0] * H), int(band[1] * H))
        if r: res[str(i)] = r
        i += 1
    json.dump(res, open(outp, "w"))
    print(src, "frames", i, "with pills", len(res))
