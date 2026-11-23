"""Extra LaMa masks for video50: enzyme labels (static rects) and cyan offer pills (colour-detected)."""
import json, subprocess, numpy as np, cv2, sys
S = sys.argv[1]
W, H = 720, 1280; fps = 2997 / 125
extra = {}
def add(f, r): extra.setdefault(f, []).append([int(v) for v in r])
# enzyme labels: (first, last frame, rect)
for a, b, r in [(1503, 1554, [188, 726, 532, 798]), (1622, 1724, [180, 726, 542, 798]), (1747, 1844, [242, 726, 482, 798])]:
    for f in range(a, b + 1): add(f, r)
# cyan pills between 98.5 and 102.5 s
f0, f1 = int(98.5 * fps), int(102.5 * fps)
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str((f0 - 0.5) / fps), '-i', f'{S}/src/video50.mp4', '-frames:v', str(f1 - f0),
                      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
cy = {}
for k in range(f1 - f0):
    fr = np.frombuffer(p.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3).astype(int)
    m = ((fr[:, :, 0] < 110) & (fr[:, :, 1] > 160) & (fr[:, :, 2] > 160) & (fr[:, :, 2] - fr[:, :, 0] > 90)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    boxes = []
    for j in range(1, n):
        x, y, w, h, a = st[j]
        if a < 400 or w < 40: continue
        boxes.append([int(x) - 5, int(y) - 5, int(x + w) + 5, int(y + h) + 5])
        add(f0 + k, boxes[-1])
    cy[f0 + k] = boxes
json.dump({str(k): v for k, v in cy.items()}, open(f'{S}/tmp/video50_cyan.json', 'w'))
for f in sorted(cy):
    if cy[f]: print(f, round(f / fps, 2), cy[f])
d = json.load(open(f'{S}/tmp/video50_masks_p1orig.json'))
for f, rs in extra.items():
    d.setdefault(str(f), []).extend(rs)
json.dump(d, open(f'{S}/tmp/video50_masks.json', 'w'))
print('frames with extra masks', len(extra), 'total masked frames', len(d))
