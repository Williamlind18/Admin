"""Re-inpaint some frame ranges from the source with corrected masks and splice them into a cleaned video.
usage: redo_ranges.py SRC CLEAN masks_fixed.json OUT a-b,c-d,...   (inclusive frame ranges)"""
import sys, json, subprocess, os, numpy as np
src, clean, mfix, out, rng = sys.argv[1:6]
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAMA = '/home/user/Admin/.claude/skills/ad-video-localizer/scripts/lama_inpaint.py'
MODEL = os.path.join(os.path.dirname(S), 'lama_model', 'big-lama.pt')
ranges = [tuple(int(x) for x in r.split('-')) for r in rng.split(',')]
tmpd = out + '_parts'; os.makedirs(tmpd, exist_ok=True)
parts = []
for a, b in ranges:
    p = f'{tmpd}/{a}_{b}.mp4'
    subprocess.run(['python3', LAMA, src, mfix, p, '--model', MODEL, '--start', str(a), '--end', str(b + 1), '--crf', '12'],
                   check=True, env={**os.environ, 'LAMA_THREADS': os.environ.get('LAMA_THREADS', '2')})
    parts.append((a, b, p))
pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate',
                                '-of', 'json', clean], capture_output=True, text=True).stdout)['streams'][0]
W, H, R = pr['width'], pr['height'], pr['r_frame_rate']
n = W * H * 3
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', clean, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', R, '-i', '-',
                        '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
pd = {}
for a, b, p in parts:
    d = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', p, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    for f in range(a, b + 1):
        pd[f] = d.stdout.read(n)
    d.wait()
f = 0
while True:
    buf = dec.stdout.read(n)
    if len(buf) < n: break
    enc.stdin.write(pd[f] if f in pd and len(pd[f]) == n else buf)
    f += 1
enc.stdin.close(); enc.wait()
print('frames', f, 'replaced', sum(1 for k in pd if len(pd[k]) == n))
