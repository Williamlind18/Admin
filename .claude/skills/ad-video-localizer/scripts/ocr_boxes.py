"""OCR of burned-in captions in white boxes. Usage: python3 ocr_boxes.py VIDEO OUT.json [FPS]
Finds white rectangles (closing fills the text), OCRs each crop with tesseract, writes per-sample results."""
import json, os, subprocess, sys
os.environ["OMP_THREAD_LIMIT"] = "1"
from concurrent.futures import ThreadPoolExecutor
import cv2, numpy as np, imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
src, out = sys.argv[1], sys.argv[2]
fps = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
W, H = 720, 1280
p = subprocess.run([FF, "-v", "error", "-i", src, "-vf", f"fps={fps},format=rgb24", "-f", "rawvideo", "-"], capture_output=True)
frames = np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W, 3)

def boxes(img):
    white = (img.min(axis=2) > 225).astype(np.uint8) * 255
    closed = cv2.morphologyEx(white, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 5)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(closed)
    res = []
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if 60 <= w <= 700 and 18 <= h <= 140 and area / (w * h) > 0.85 and w > 1.6 * h:
            crop = img[y:y + h, x:x + w]
            dark = (crop.max(axis=2) < 110).mean()
            if 0.02 < dark < 0.5:
                res.append((int(x), int(y), int(w), int(h)))
    return res

def ocr(crop):
    g = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    g = cv2.resize(g, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    _, g = cv2.threshold(g, 150, 255, cv2.THRESH_BINARY)
    ok, png = cv2.imencode(".png", g)
    r = subprocess.run(["tesseract", "stdin", "stdout", "--psm", "6", "-l", "eng"], input=png.tobytes(), capture_output=True)
    return " ".join(r.stdout.decode("utf-8", "ignore").split())

def work(k):
    img = frames[k]
    items = []
    for (x, y, w, h) in boxes(img):
        t = ocr(img[y:y + h, x:x + w])
        if len(t) >= 2:
            items.append({"box": [x, y, w, h], "text": t})
    return {"t": round(k / fps, 3), "items": items}

with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(work, range(len(frames))))
json.dump(res, open(out, "w"), indent=0)
print(len(res), "samples")
