"""Third pass for Vmake leftovers: thin white lines (the top/bottom edge of an emptied caption pill) in the cleaned video,
kept only where the source shows caption text right there. usage: vmake_lines.py SRC CLEAN OUT_masks.json"""
import sys, json, subprocess, numpy as np, cv2
src, cl, out = sys.argv[1:4]
W, H = 720, 900; n = W * H * 3
def rd(p): return subprocess.Popen(['ffmpeg', '-v', 'error', '-i', p, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
a, b = rd(src), rd(cl); f = 0; masks = {}
while True:
    x = a.stdout.read(n); y = b.stdout.read(n)
    if len(x) < n or len(y) < n: break
    I = np.frombuffer(x, np.uint8).reshape(H, W, 3); C = np.frombuffer(y, np.uint8).reshape(H, W, 3)
    gc = cv2.cvtColor(C, cv2.COLOR_BGR2GRAY); sc = cv2.cvtColor(C, cv2.COLOR_BGR2HSV)[:, :, 1]
    # bright thin horizontal structures: much brighter than the local background
    bg = cv2.blur(gc, (1, 21)).astype(np.int16)
    line = ((gc.astype(np.int16) - bg > 35) & (gc > 185) & (sc < 60)).astype(np.uint8)
    line = cv2.morphologyEx(line, cv2.MORPH_CLOSE, np.ones((1, 9), np.uint8))
    nn, lab, st, _ = cv2.connectedComponentsWithStats(line)
    gi = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
    boxes = []
    for j in range(1, nn):
        x0, y0, w, h, ar = st[j]
        if w < 70 or h > 10: continue
        ok = False
        for r0, r1 in ((y0 + h, y0 + h + 30), (y0 - 30, y0)):
            reg = gi[max(0, r0):max(0, r1), x0:x0 + w]
            if reg.size and (reg > 205).mean() > 0.45 and (reg < 90).mean() > 0.02: ok = True
        if not ok: continue
        boxes.append([x0, y0, x0 + w, y0 + h])
    # merge lines into pill-sized boxes
    boxes.sort(key=lambda r: r[1]); merged = []
    for r in boxes:
        if merged and r[1] - merged[-1][3] < 60 and not (r[2] < merged[-1][0] or merged[-1][2] < r[0]):
            m = merged[-1]; merged[-1] = [min(m[0], r[0]), min(m[1], r[1]), max(m[2], r[2]), max(m[3], r[3])]
        else: merged.append(list(r))
    if merged:
        masks[str(f)] = [[int(max(0, m[0] - 10)), int(max(0, m[1] - 12)), int(min(W, m[2] + 10)), int(min(H, m[3] + 12))] for m in merged]
    f += 1
json.dump(masks, open(out, 'w')); print('frames', f, 'frames with lines', len(masks))
