"""grid.py img out x0 y0 x1 y1 [step]: crop with a labelled coordinate grid (full-res coords) for picking corners."""
import sys
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert("RGB"); x0, y0, x1, y1 = map(int, sys.argv[3:7]); st = int(sys.argv[7]) if len(sys.argv) > 7 else 50
c = im.crop((x0, y0, x1, y1)); sc = 900 / max(c.size); c = c.resize((int(c.width * sc), int(c.height * sc)))
d = ImageDraw.Draw(c); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13) if True else None
for x in range((x0 // st + 1) * st, x1, st):
    X = (x - x0) * sc; d.line([(X, 0), (X, c.height)], fill=(255, 0, 0) if x % (st * 2) == 0 else (255, 150, 150), width=1); d.text((X + 2, 2), str(x), fill=(255, 0, 0), font=f)
for y in range((y0 // st + 1) * st, y1, st):
    Y = (y - y0) * sc; d.line([(0, Y), (c.width, Y)], fill=(0, 0, 255) if y % (st * 2) == 0 else (150, 150, 255), width=1); d.text((2, Y + 2), str(y), fill=(0, 0, 255), font=f)
c.save(sys.argv[2])
