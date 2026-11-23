"""Assets for the v49 offer graphic: title lines (KÖP 2 / FÅ 2 / GRATIS) and the guarantee box."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/up/tools')
from gfx import *
from PIL import Image, ImageDraw
S = '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/up'
def title_line(txt, cap, fontname='kanit_xbi'):
    """White title line at 2x resolution (for clean downscaling), with soft shadow; returns (img, cap_center_offset)."""
    k = 2
    f = font(fontname, 20)
    f = font(fontname, 20 * cap * k / cap_height(f))
    t = text_layer(txt, f, fill=(255, 255, 255, 255), pad=30)
    sh, m = shadow(t, radius=5, offset=(3, 5), opacity=0.35)
    # cap centre: bbox of the letter H height relative to baseline -> use ink bbox of the text without accents
    rep = txt.replace('Ö', 'O').replace('Å', 'A')
    x0, y0, x1, y1 = ink_bbox(text_layer(rep, f, pad=30))
    d = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    rb = d.textbbox((0, 0), txt, font=f); pb = d.textbbox((0, 0), rep, font=f)
    dx, dy = pb[0] - rb[0], pb[1] - rb[1]
    return sh, ((x0 + x1) / 2 + dx + m, (y0 + y1) / 2 + dy + m), k
def box(text='30 dagars pengarna tillbaka'):
    k = 2
    W, H, R = 441 * k, 108 * k, 18 * k
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W - 1, H - 1], R, fill=(255, 255, 255, 255))
    col = (139, 112, 74, 255); lw = 2 * k
    # banknote icon at x 178-216, y 667-705 in frame -> box-relative (39..77, 34..72)
    ox, oy = 39 * k, 37 * k
    for i, dx in enumerate((10, 5)):
        d.line([(ox + dx * k, oy + 8 * k - i * 3 * k), (ox + dx * k + 26 * k, oy + 2 * k - i * 3 * k)], fill=col, width=lw)
    d.rounded_rectangle([ox, oy + 9 * k, ox + 38 * k, oy + 33 * k], 2 * k, outline=col, width=lw, fill=(255, 255, 255, 255))
    d.rounded_rectangle([ox + 4 * k, oy + 13 * k, ox + 34 * k, oy + 29 * k], 6 * k, outline=col, width=lw)
    fk = font('pop_sb', 10 * k)
    tw = d.textlength('kr', font=fk)
    d.text((ox + 19 * k - tw / 2, oy + 13 * k), 'kr', font=fk, fill=col)
    f = font('pop_sb', 16.5 * k)
    bb = d.textbbox((0, 0), 'H', font=f)
    ch = bb[3] - bb[1]
    d.text((98 * k, H / 2 - ch / 2 - bb[1]), text, font=f, fill=(51, 51, 51, 255))
    sh, m = shadow(im, radius=6, offset=(0, 4), opacity=0.25)
    return sh, (m + W / 2, m + H / 2), k
if __name__ == '__main__':
    import numpy as np
    fr = np.array(Image.open(f'{S}/tmp/fr/v49_95.4.png').convert('RGB'))
    for txt, cap, cy in (('KÖP 2', 55, 582), ('FÅ 2', 68, 659), ('GRATIS', 84, 752)):
        im, (cx0, cy0), k = title_line(txt, cap)
        im2 = im.resize((im.width // k, im.height // k), Image.LANCZOS)
        composite(fr, im2, 362 - cx0 / k + 160, cy - cy0 / k)
    b, (bx, by), k = box()
    b2 = b.resize((b.width // k, b.height // k), Image.LANCZOS)
    composite(fr, b2, 360 - bx / k, 1000 - by / k)
    Image.fromarray(fr).crop((0, 450, 720, 1100)).save(f'{S}/tmp/assets49_test.png')
