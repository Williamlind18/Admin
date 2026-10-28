import sys, json; sys.path.insert(0, '.')
import numpy as np
from PIL import Image, ImageDraw
from frames import get_frames
import anim
SHOW = json.load(open('show.json'))
test = [int(x) for x in sys.argv[1].split(',')]
out = sys.argv[2]
keys = sorted(set(it['n'] for it in anim.ITEMS if it['id'] in anim.TR))
FR = get_frames('dl/src_orig.mp4', keys + test)
items = []
for it in anim.ITEMS:
    if it['id'] not in anim.TR: continue
    I = anim.Item(it, FR[it['n']]); I.show = {int(k): v for k, v in SHOW.get(it['id'], {}).items()}; items.append(I)
tiles = []
for n in test:
    o = anim.render(FR[n], n, items)
    a = Image.fromarray(np.hstack([FR[n][150:780], o[150:780]])).resize((720, 315))
    d = ImageDraw.Draw(a); d.rectangle([0, 0, 34, 11], fill=(0, 0, 0)); d.text((2, 0), str(n), fill=(255, 255, 0))
    tiles.append(a)
cols = 2
rows = (len(tiles) + cols - 1) // cols
g = Image.new('RGB', (cols * 722, rows * 317), (80, 80, 80))
for i, t in enumerate(tiles): g.paste(t, ((i % cols) * 722, (i // cols) * 317))
g.save(out)
