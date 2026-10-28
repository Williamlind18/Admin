import subprocess, numpy as np, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
def get_frames(path, ns, W=720, H=1280):
    """Decode the given frame numbers (sorted, one decode pass)."""
    ns = sorted(set(ns)); out = {}
    sel = '+'.join(f'eq(n\\,{n})' for n in ns)
    p = subprocess.Popen([FF, '-v', 'error', '-i', path, '-vf', f"select='{sel}'", '-fps_mode', 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    for n in ns:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        out[n] = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    p.stdout.close(); p.wait()
    return out
