"""QA sheet: Swedish source | clean + Danish overlays, at given times (default: mid of each item)."""
import sys, json, io, subprocess
from PIL import Image, ImageDraw
k = sys.argv[1]; spec = json.load(open(f"ov/{k}/spec.json"))
def fr(p, t):
    o = subprocess.run(["ffmpeg","-nostdin","-v","error","-ss",f"{t:.3f}","-i",p,"-frames:v","1","-f","image2pipe","-vcodec","png","-"],capture_output=True).stdout
    return Image.open(io.BytesIO(o)).convert("RGBA")
times = [float(x) for x in sys.argv[3:]] or sorted({round((it["t0"] + min(it["t1"], it["t0"] + 3)) / 2, 2) for it in spec["items"]})
tiles = []
for t in times:
    src = fr(f"vid/{k}.mp4", t); cl = fr(f"clean/{k}_clean.mp4", t)
    for it in spec["items"]:
        if not (it["t0"] <= t < it["t1"]): continue
        if it["kind"] == "png": cl.alpha_composite(Image.open(it["file"]).convert("RGBA"))
        elif it["kind"] == "src":
            x0, y0, x1, y1 = it["box"]; cl.paste(src.crop((x0, y0, x1, y1)), (x0, y0))
        elif it["kind"] == "seq":
            i = min(it["n"] - 1, int((t - it["t0"]) * 30 + 1e-6)); cl.alpha_composite(Image.open(it["pattern"] % i).convert("RGBA"))
    w = 300; h = int(src.size[1] * w / src.size[0])
    pair = Image.new("RGB", (2 * w, h)); pair.paste(src.resize((w, h)).convert("RGB"), (0, 0)); pair.paste(cl.resize((w, h)).convert("RGB"), (w, 0))
    ImageDraw.Draw(pair).text((4, 4), f"{t}", fill=(255, 255, 0))
    tiles.append(pair)
cols = 3; rows = (len(tiles) + cols - 1) // cols
W, H = tiles[0].size
sheet = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
for i, tl in enumerate(tiles): sheet.paste(tl, ((i % cols) * W, (i // cols) * H))
sheet.save(sys.argv[2]); print(len(tiles), "tiles")
