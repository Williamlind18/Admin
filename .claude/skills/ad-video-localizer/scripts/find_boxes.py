"""Find centred white caption boxes in every frame. Usage: python3 find_boxes.py VIDEO OUT.json"""
import json, subprocess, sys
import cv2, numpy as np, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 720, 1280
p = subprocess.Popen([FF, "-v", "error", "-i", sys.argv[1], "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
res = []; i = 0
while True:
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    white = (img.min(axis=2) > 215).astype(np.uint8) * 255
    closed = cv2.morphologyEx(white, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (11, 7)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(closed)
    bl = []
    for k in range(1, n):
        x, y, w, h, area = [int(v) for v in st[k]]
        if 60 <= w <= 640 and 22 <= h <= 100 and area / (w * h) > 0.8 and abs(x + w / 2 - 360) < 45:
            crop = img[y:y + h, x:x + w]
            dark = float((crop.max(axis=2) < 110).mean())
            if 0.03 < dark < 0.45:
                bl.append([x, y, w, h])
    res.append(bl); i += 1
json.dump({"fps": 30.0, "W": W, "H": H, "frames": res}, open(sys.argv[2], "w"))
print(i, "frames,", sum(1 for b in res if b), "with boxes")
