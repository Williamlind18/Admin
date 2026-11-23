"""Swedish enzyme titles for video56 (white Poppins Bold with a soft white glow, like the original)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import *
from PIL import Image, ImageDraw
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
f = font('pop_b', 60); size = 60 * 545 / d.textlength('Alpha-amylase', font=f)
f = font('pop_b', size)
for name, txt in (('alfa', 'Alfa-amylas'), ('proteas', 'Proteas'), ('lipas', 'Lipas')):
    t = text_layer(txt, f, fill=(255, 255, 255, 255), pad=40)
    g, m = glow(t, 14, (255, 255, 255), 0.55, spread=3)
    g2, m2 = glow(t, 5, (0, 0, 0), 0.25)
    lay = Image.new('RGBA', g.size, (0, 0, 0, 0)); lay.alpha_composite(g); lay.alpha_composite(g2, (m - m2, m - m2)); lay.alpha_composite(t, (m, m))
    x0, y0, x1, y1 = ink_bbox(text_layer(txt.replace('y', 'v').replace('p', 'n'), f, pad=40))
    canvas = Image.new('RGBA', (720, 900), (0, 0, 0, 0))
    canvas.alpha_composite(lay, (int(360 - ((x0 + x1) / 2 + m)), int(134 - ((y0 + y1) / 2 + m))))
    canvas.save(f'{S}/tmp/title56_{name}.png')
print('ok', round(size, 1))
