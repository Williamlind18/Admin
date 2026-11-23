import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/up/tools')
from gfx import *
from PIL import Image
import numpy as np, cv2
S = '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/up'
rgba = np.array(Image.open(f'{S}/tmp/badge49_raw.png')).astype(np.float32)
rgba[:10, :, 3] = 0
rgb = rgba[:, :, :3].astype(np.uint8).copy()
mask = np.zeros(rgb.shape[:2], np.uint8)
for x0, y0, x1, y1 in [(86, 58, 154, 89), (196, 44, 326, 88), (146, 98, 350, 142)]:
    sub = rgb[y0:y1, x0:x1].astype(int)
    m = (sub.min(2) > 200)
    mask[y0:y1, x0:x1] |= m.astype(np.uint8)
mask = cv2.dilate(mask, np.ones((7, 7), np.uint8))
rgb2 = cv2.inpaint(rgb, mask * 255, 6, cv2.INPAINT_TELEA)
# smooth the filled area a little
bl = cv2.GaussianBlur(rgb2, (0, 0), 2.5)
mm = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 1.5)[..., None]
rgb3 = (bl * mm + rgb2 * (1 - mm)).astype(np.uint8)
base = Image.fromarray(np.dstack([rgb3, rgba[:, :, 3].astype(np.uint8)]))
def put(img, txt, cap, cx, cy, ang):
    f = font('pop_xb', 10)
    f = font('pop_xb', 10 * cap / cap_height(f))
    t = text_layer(txt, f, fill=(255, 255, 255, 255))
    sh = text_layer(txt, f, fill=(46, 128, 214, 255))
    lay = Image.new('RGBA', (t.width + 4, t.height + 4), (0, 0, 0, 0))
    lay.alpha_composite(sh, (2, 3)); lay.alpha_composite(t, (0, 0))
    lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    x0, y0, x1, y1 = ink_bbox(lay)
    img.alpha_composite(lay, (int(round(cx - (x0 + x1) / 2)), int(round(cy - (y0 + y1) / 2))))
put(base, 'FRI', 21, 120, 73, 5)
put(base, 'FRI', 33, 261, 66, 4)
put(base, 'FRAKT', 29, 248, 120, 2)
base.save(f'{S}/tmp/badge49_sv.png')
pv = Image.new('RGBA', base.size, (60, 60, 60, 255)); pv.alpha_composite(base); pv.resize((base.width * 2, base.height * 2)).save(f'{S}/tmp/badge49_sv_pv.png')
