"""Closing-card patch: a short dip from the last footage frame into our offer image, then a slow zoom.
usage: card_patch.py OUT.mp4 NFRAMES FPS SRC.mp4 PREV_FRAME"""
import sys, subprocess, numpy as np
from PIL import Image
out, nf, fps, src, prevf = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], int(sys.argv[5])
S = '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/up'
W, H = 720, 1280
CARD = Image.open(f'{S}/tmp/endcard_sv.png').convert('RGB')
fr = eval(fps)
p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str((prevf - 0.5) / fr), '-i', src, '-frames:v', '1', '-fps_mode', 'passthrough',
                    '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
prev = np.frombuffer(p.stdout[:W * H * 3], np.uint8).reshape(H, W, 3).astype(np.float32)
enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', fps, '-i', '-',
                        '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
for k in range(nf):
    t = k / max(1, nf - 1)
    z = 1.0 + 0.04 * t
    cw, ch = CARD.width / z, CARD.height / z
    x0, y0 = (CARD.width - cw) / 2, (CARD.height - ch) / 2
    im = np.asarray(CARD.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)).astype(np.float32)
    if k < 2:            # flash to white like the original's cut
        a = (k + 1) / 3; im = prev * (1 - a) + 255 * a
    elif k < 6:
        a = (k - 1) / 5; im = 255 * (1 - a) + im * a
    enc.stdin.write(im.clip(0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print('ok', nf)
