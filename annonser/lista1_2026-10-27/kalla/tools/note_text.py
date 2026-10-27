"""Render handwritten post-it text in HTML (headless Chrome, transparent) and warp it onto real notes in a photo.

notes.json: {"photo": "...", "out": "...", "notes": [{"quad": [[x,y]*4 TL,TR,BR,BL], "html": "..."}]}
The text is set by the browser (crisp, correctly spelled) and then follows each note's perspective;
it is multiplied onto the paper so the note's own light and shadow stay.
"""
import json, os, pathlib, subprocess, sys
import cv2
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
CHROME = str(HERE / "chrome.sh")
FONTS = "file://" + str(HERE.parent / "fonts" / "local.css")
SIDE = 600  # note texture size in px (square)


def render_note(html, out_png):
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>@import url("{FONTS}");
    *{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:{SIDE}px;height:{SIDE}px;background:transparent;overflow:hidden}}
    .n{{position:absolute;inset:0;padding:40px 38px 52px;display:flex;flex-direction:column;justify-content:center;
        font-family:'Patrick Hand';font-size:140px;line-height:1.02;color:#1b1b1b}}
    .n .big{{color:#D9161C;font-size:144px}} .n .s{{font-size:96px}}
    </style></head><body><div class="n">{html}</div>
    <script>document.fonts.ready.then(()=>{{const n=document.querySelector('.n');let s=140;
      while((n.scrollHeight>n.clientHeight+1||n.scrollWidth>n.clientWidth+1)&&s>40){{s*=.96;n.style.fontSize=s+'px';
      n.querySelectorAll('.big').forEach(e=>e.style.fontSize=(s*1.03)+'px');n.querySelectorAll('.s').forEach(e=>e.style.fontSize=(s*.82)+'px');}}}});</script>
    </body></html>"""
    src = pathlib.Path(out_png).with_suffix(".html")
    src.write_text(page, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                    f"--window-size={SIDE},{SIDE}", "--virtual-time-budget=5000", f"--screenshot={out_png}", src.as_uri()],
                   check=True, capture_output=True)


def main(spec):
    spec = json.loads(pathlib.Path(spec).read_text(encoding="utf-8"))
    photo = np.asarray(Image.open(spec["photo"]).convert("RGB")).astype(np.float32) / 255
    H, W = photo.shape[:2]
    tmp = pathlib.Path(spec["out"]).parent / "_notes"
    tmp.mkdir(parents=True, exist_ok=True)
    for i, n in enumerate(spec["notes"]):
        png = tmp / f"note{i}.png"
        render_note(n["html"], str(png))
        t = np.asarray(Image.open(png).convert("RGBA")).astype(np.float32) / 255
        M = cv2.getPerspectiveTransform(np.float32([[0, 0], [SIDE, 0], [SIDE, SIDE], [0, SIDE]]), np.float32(n["quad"]))
        rgb = cv2.warpPerspective(t[..., :3], M, (W, H), flags=cv2.INTER_AREA)
        a = cv2.warpPerspective(t[..., 3], M, (W, H), flags=cv2.INTER_AREA) * n.get("ink", 0.93)
        a = cv2.GaussianBlur(a, (0, 0), 0.5)  # marker ink is never razor sharp
        # multiply: ink darkens the paper, the paper's light/shadow stays visible through it
        photo = photo * (1 - a[..., None]) + (photo * rgb) * a[..., None]
    Image.fromarray(np.clip(photo * 255, 0, 255).astype(np.uint8)).save(spec["out"])
    print("ok", spec["out"])


if __name__ == "__main__":
    main(sys.argv[1])
