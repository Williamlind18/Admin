"""Per-frame masks for white caption boxes (black text) burned into an original. usage: capmasks.py SRC OUT.json Y0 Y1"""
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
    white = ((hsv[:,:,2] > 225) & (hsv[:,:,1] < 30)).astype(np.uint8)
    white = cv2.morphologyEx(white, cv2.MORPH_CLOSE, np.ones((7,15),np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(white)
    rects = []
    for j in range(1, n):
        x, y, w, h, a = st[j]
        if w < 40 or h < 14 or h > 0.12*H or w/h < 1.8 or a < 0.75*w*h: continue
        g = cv2.cvtColor(img[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
        dark = (g < 90).mean()
        if 0.03 < dark < 0.45:   # text inside
            rects.append([int(x-4), int(Y0+y-4), int(x+w+4), int(Y0+y+h+4)])
    if rects: masks[i] = rects
    i += 1
json.dump(masks, open(out, "w"))
fr = sorted(masks); print(len(masks), "frames with boxes of", i, "first", fr[:1], "last", fr[-1:])
