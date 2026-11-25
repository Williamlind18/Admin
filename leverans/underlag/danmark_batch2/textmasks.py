"""Masks for white caption words with a black outline (our own burned-in captions) in the band Y0-Y1.
usage: textmasks.py SRC OUT.json Y0 Y1"""
import sys, json, subprocess, numpy as np, cv2
src, out, y0f, y1f = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
o = json.loads(subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","json",src],capture_output=True,text=True).stdout)["streams"][0]
W, H = o["width"], o["height"]; Y0, Y1 = int(y0f*H), int(y1f*H)
pr = subprocess.Popen(["ffmpeg","-nostdin","-v","error","-i",src,"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
masks = {}; i = 0
while True:
    b = pr.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    img = np.frombuffer(b,np.uint8).reshape(H,W,3)[Y0:Y1]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    white = ((hsv[:,:,2] > 215) & (hsv[:,:,1] < 40)).astype(np.uint8)
    dark = cv2.dilate((hsv[:,:,2] < 60).astype(np.uint8), np.ones((7,7),np.uint8))
    txt = white & dark                      # white strokes next to a black outline
    txt = cv2.morphologyEx(txt, cv2.MORPH_CLOSE, np.ones((15,45),np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(txt)
    rects = []
    for j in range(1, n):
        x, y, w, h, a = st[j]
        if a < 300 or h < 20: continue
        rects.append([int(x-12), int(Y0+y-12), int(x+w+12), int(Y0+y+h+12)])
    if rects: masks[i] = rects
    i += 1
json.dump(masks, open(out, "w"))
print(len(masks), "of", i, "frames masked; sample", {k: masks[k] for k in list(masks)[:2]})
