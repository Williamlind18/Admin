"""Render a sale tape in HTML in the box-front's own coordinates and lay it onto the box in the photo, lit by the photo."""
import json, pathlib, subprocess, sys
import cv2, numpy as np
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import boxlib
HERE = pathlib.Path(__file__).resolve().parent
spec = json.load(open(sys.argv[1]))
photo = np.asarray(Image.open(spec["photo"]).convert("RGB")).astype(np.float32)
H, W = photo.shape[:2]
q = np.float32(spec["quad"]); fw, fh = spec["w"], spec["h"]
html = pathlib.Path(spec["out"]).resolve().with_suffix(".tape.html")
fonts = (HERE.parent / "fonts" / "all.css").as_uri()
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@import url("{fonts}");*{{margin:0;padding:0;box-sizing:border-box}}'
                f'html,body{{width:{fw}px;height:{fh}px;background:transparent;overflow:hidden}}body{{position:relative}}{spec["css"]}</style></head>'
                f'<body>{spec["body"]}</body></html>', encoding="utf-8")
png = html.with_suffix(".png")
subprocess.run([str(HERE / "chrome.sh"), "--headless", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                f"--window-size={fw},{fh}", "--virtual-time-budget=6000", f"--screenshot={png}", html.as_uri()], check=True, capture_output=True)
t = np.asarray(Image.open(png).convert("RGBA")).astype(np.float32)
ss = 2
M = cv2.getPerspectiveTransform(np.float32([[0, 0], [fw, 0], [fw, fh], [0, fh]]), q * ss)
rgb = cv2.warpPerspective(t[..., :3] * (t[..., 3:] / 255), M, (W * ss, H * ss), flags=cv2.INTER_LINEAR)
a = cv2.warpPerspective(t[..., 3] / 255, M, (W * ss, H * ss), flags=cv2.INTER_LINEAR)
rgb = cv2.resize(rgb, (W, H), interpolation=cv2.INTER_AREA); a = cv2.resize(a, (W, H), interpolation=cv2.INTER_AREA)
rgb = np.where(a[..., None] > 1e-3, rgb / np.maximum(a[..., None], 1e-3), 0)
# light: photo luminance, very smooth, relative to the face's bright paper level
lum = photo @ np.float32([.299, .587, .114])
fm = np.zeros((H, W), np.float32); cv2.fillPoly(fm, [np.int32(q)], 1)
ref = np.percentile(lum[fm > 0], 90)
shade = cv2.GaussianBlur(lum * fm, (0, 0), 25) / np.maximum(cv2.GaussianBlur(fm, (0, 0), 25), 1e-3) / ref
shade = np.clip(shade, 0.55, 1.08)[..., None]
# thin shadow under the tape's lower edge (tape thickness)
sh = cv2.GaussianBlur(np.roll(a, spec.get("shadow_dy", 3), 0), (0, 0), 3) * (1 - a) * 0.28
out = photo * (1 - sh[..., None])
out = out * (1 - a[..., None]) + rgb * shade * a[..., None]
rng = np.random.default_rng(5); out += rng.normal(0, 2.0, out.shape) * a[..., None]
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(spec["out"]); print("ok", spec["out"])
