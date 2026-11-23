"""Build the final caption-free picture: base clean video + spliced patch videos + static overlays.
usage: assemble.py BASE OUT --fps F [--patch file:start ...] [--overlay png:f0-f1 ...] [--hold SECONDS]"""
import sys, subprocess, argparse, numpy as np, json
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument('base'); ap.add_argument('out'); ap.add_argument('--fps', required=True)
ap.add_argument('--patch', action='append', default=[]); ap.add_argument('--overlay', action='append', default=[])
ap.add_argument('--hold', type=float, default=0.0)
a = ap.parse_args()
W, H = 720, 1280; n = W * H * 3
def reader(p):
    pr = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', p, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        b = pr.stdout.read(n)
        if len(b) < n: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
patches = []
for p in a.patch:
    f, s = p.rsplit(':', 1); patches.append((int(s), f))
pd = {}
for s, f in patches:
    for k, fr in enumerate(reader(f)): pd[s + k] = fr
ovs = []
for o in a.overlay:
    f, r = o.rsplit(':', 1); f0, f1 = [int(x) for x in r.split('-')]
    im = np.asarray(Image.open(f).convert('RGBA')).astype(np.float32)
    ovs.append((f0, f1, im[:, :, :3], im[:, :, 3:4] / 255))
enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', a.fps, '-i', '-',
                        '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', a.out], stdin=subprocess.PIPE)
f = 0; last = None; used = 0
for fr in reader(a.base):
    img = pd.get(f, fr)
    if f in pd: used += 1
    for f0, f1, rgb, al in ovs:
        if f0 <= f <= f1:
            img = (rgb * al + img * (1 - al)).round().astype(np.uint8)
    enc.stdin.write(np.ascontiguousarray(img).tobytes()); last = img; f += 1
fps = eval(a.fps)
for _ in range(int(round(a.hold * fps))):
    enc.stdin.write(last.tobytes()); f += 1
enc.stdin.close(); enc.wait()
print('frames', f, 'patched', used, 'of', len(pd))
