"""Set text in HTML (headless Chrome, transparent), then lay it onto a flat object in a photo (sign, card, note).
Usage: warp_html.py SPEC.json  -> {"photo","out","out_size":[w,h],"items":[{"quad":[[x,y]x4 TL,TR,BR,BL],"w","h","css","body"}]}"""
import json, pathlib, subprocess, sys
import cv2
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
CHROME = str(HERE / "chrome.sh")
FONTS = (HERE.parent / "fonts" / "all.css").as_uri()


def render(item, png):
    w, h = item["w"], item["h"]
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>@import url("{FONTS}");'
            f'*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:{w}px;height:{h}px;background:transparent;overflow:hidden}}'
            f'body{{position:relative}}{item["css"]}</style></head><body>{item["body"]}</body></html>')
    src = pathlib.Path(png).with_suffix(".html")
    src.write_text(html, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                    f"--window-size={w},{h}", "--virtual-time-budget=6000", f"--screenshot={png}", src.as_uri()],
                   check=True, capture_output=True)


def main(spec_path):
    spec = json.loads(pathlib.Path(spec_path).read_text(encoding="utf-8"))
    photo = np.asarray(Image.open(spec["photo"]).convert("RGB")).astype(np.float32) / 255
    H, W = photo.shape[:2]
    tmp = pathlib.Path(spec["out"]).parent / "_warp"
    tmp.mkdir(parents=True, exist_ok=True)
    for i, it in enumerate(spec["items"]):
        png = tmp / f"{pathlib.Path(spec['out']).stem}_{i}.png"
        render(it, str(png))
        t = np.asarray(Image.open(png).convert("RGBA")).astype(np.float32) / 255
        M = cv2.getPerspectiveTransform(np.float32([[0, 0], [it["w"], 0], [it["w"], it["h"]], [0, it["h"]]]), np.float32(it["quad"]))
        rgb = cv2.warpPerspective(t[..., :3], M, (W, H), flags=cv2.INTER_AREA)
        a = cv2.warpPerspective(t[..., 3], M, (W, H), flags=cv2.INTER_AREA) * it.get("ink", 0.95)
        a = cv2.GaussianBlur(a, (0, 0), 0.6)
        photo = photo * (1 - a[..., None]) + (photo * rgb) * a[..., None]   # printed ink: multiply onto the paper
    img = Image.fromarray(np.clip(photo * 255, 0, 255).astype(np.uint8))
    if spec.get("out_size"):
        img = img.resize(tuple(spec["out_size"]), Image.LANCZOS)
    img.save(spec["out"])
    print("ok", spec["out"], img.size)


if __name__ == "__main__":
    main(sys.argv[1])
