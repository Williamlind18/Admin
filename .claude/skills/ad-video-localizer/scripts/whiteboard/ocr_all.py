# OCR every frame of the animation (frames A..B) above the caption band; one JSON line per frame.
import sys, subprocess, json, numpy as np, imageio_ffmpeg, pytesseract
from PIL import Image
from multiprocessing import Pool
FF = imageio_ffmpeg.get_ffmpeg_exe()
A, B, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
W, H, YMAX = 720, 1280, 785
def frames():
    p = subprocess.Popen([FF, '-v', 'error', '-i', 'dl/src_orig.mp4', '-vf', f"select='between(n\\,{A}\\,{B})'", '-fps_mode', 'passthrough',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    n = A
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield n, np.frombuffer(b, np.uint8).reshape(H, W, 3)[:YMAX].copy()
        n += 1
def ocr(item):
    n, f = item
    g = Image.fromarray(f).convert('L').resize((W * 2, YMAX * 2), Image.LANCZOS)
    d = pytesseract.image_to_data(g, config='--psm 11', output_type=pytesseract.Output.DICT)
    ws = [[d['text'][i], int(float(d['conf'][i])), d['left'][i] / 2, d['top'][i] / 2, d['width'][i] / 2, d['height'][i] / 2]
          for i in range(len(d['text'])) if d['text'][i].strip() and float(d['conf'][i]) >= 60]
    return n, ws
with Pool(4) as pool, open(out, 'w') as fh:
    for n, ws in pool.imap(ocr, frames(), chunksize=4):
        fh.write(json.dumps({'n': n, 'w': ws}) + '\n')
