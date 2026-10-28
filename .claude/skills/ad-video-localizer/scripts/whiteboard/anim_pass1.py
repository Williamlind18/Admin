# Pass 1: measure every item in every animation frame, decide visibility, save to show.json
import sys, json, subprocess, numpy as np, imageio_ffmpeg
sys.path.insert(0, '.')
import anim
from frames import get_frames
FF = imageio_ffmpeg.get_ffmpeg_exe()
A, B = 214, 1773
W, H = 720, 1280
keys = sorted(set(it['n'] for it in anim.ITEMS if it['id'] in anim.TR))
KF = get_frames('dl/src_orig.mp4', keys)
items = [anim.Item(it, KF[it['n']]) for it in anim.ITEMS if it['id'] in anim.TR]
p = subprocess.Popen([FF, '-v', 'error', '-i', 'dl/src_orig.mp4', '-vf', f"select='between(n\\,{A}\\,{B})'", '-fps_mode', 'passthrough',
                      '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
n = A
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    act = [I for I in items if n in I.tr]
    if act:
        hm = anim.hand_mask(f)
        for I in act: I.measure(n, f, hm)
    n += 1
show = {}
for I in items:
    I.decide()
    show[I.id] = {str(k): v for k, v in sorted(I.show.items())}
    ks = sorted(I.show)
    print(I.id, len(ks), (ks[0], ks[-1]) if ks else '-')
json.dump(show, open('show.json', 'w'))
