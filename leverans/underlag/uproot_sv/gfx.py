"""Small graphics helpers for the Swedish overlays (PIL RGBA layers, compositing onto RGB numpy frames)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD = '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/fonts_dl'
FONTS = {
    'mont_xb': '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/v22it/fonts/Montserrat-ExtraBold.ttf',
    'mont': f'{FD}/Montserrat[wght].ttf', 'mont_i': f'{FD}/Montserrat-Italic[wght].ttf',
    'kanit_xbi': f'{FD}/Kanit-ExtraBoldItalic.ttf',
    'pop_l': f'{FD}/Poppins-Light.ttf', 'pop_r': f'{FD}/Poppins-Regular.ttf', 'pop_m': f'{FD}/Poppins-Medium.ttf',
    'pop_sb': f'{FD}/Poppins-SemiBold.ttf', 'pop_b': f'{FD}/Poppins-Bold.ttf', 'pop_xb': f'{FD}/Poppins-ExtraBold.ttf',
    'pop_xbi': f'{FD}/Poppins-ExtraBoldItalic.ttf', 'pop_bi': f'{FD}/Poppins-BoldItalic.ttf',
    'lib_b': '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
}
def font(name, size, wght=None):
    f = ImageFont.truetype(FONTS[name], int(round(size)))
    if wght is not None:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f

def text_layer(txt, fnt, fill=(255, 255, 255, 255), stroke=0, stroke_fill=None, pad=None):
    """Tight RGBA image of txt. Returns (img, (ox, oy)) where ox, oy is the offset of the ink box inside img."""
    pad = pad if pad is not None else stroke + 4
    d = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    x0, y0, x1, y1 = d.textbbox((0, 0), txt, font=fnt, stroke_width=stroke)
    im = Image.new('RGBA', (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - x0, pad - y0), txt, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def cap_height(fnt):
    d = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    b = d.textbbox((0, 0), 'H', font=fnt)
    return b[3] - b[1]

def ink_bbox(im):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1

def glow(im, radius, color, strength=1.0, spread=0):
    """A glow layer (same size as im, extra margin) made by blurring im's alpha."""
    m = radius * 3
    a = im.split()[3]
    big = Image.new('L', (im.width + 2 * m, im.height + 2 * m), 0); big.paste(a, (m, m))
    if spread: big = big.filter(ImageFilter.MaxFilter(spread * 2 + 1))
    big = big.filter(ImageFilter.GaussianBlur(radius))
    arr = (np.asarray(big).astype(np.float32) * strength).clip(0, 255).astype(np.uint8)
    g = Image.new('RGBA', big.size, color + (0,)); g.putalpha(Image.fromarray(arr))
    return g, m

def shadow(im, radius=4, offset=(2, 3), opacity=0.45):
    g, m = glow(im, radius, (0, 0, 0), opacity)
    out = Image.new('RGBA', g.size, (0, 0, 0, 0))
    out.alpha_composite(g, (offset[0], offset[1])) if offset[0] >= 0 and offset[1] >= 0 else out.alpha_composite(g)
    out.alpha_composite(im, (m, m))
    return out, m

def composite(frame, layer, x, y, opacity=1.0):
    """Alpha-composite RGBA PIL layer onto RGB uint8 numpy frame at integer/float top-left (x, y)."""
    H, W = frame.shape[:2]
    x, y = int(round(x)), int(round(y))
    L = np.asarray(layer).astype(np.float32)
    lx0, ly0 = max(0, -x), max(0, -y)
    fx0, fy0 = max(0, x), max(0, y)
    w = min(W - fx0, L.shape[1] - lx0); h = min(H - fy0, L.shape[0] - ly0)
    if w <= 0 or h <= 0: return frame
    sub = L[ly0:ly0 + h, lx0:lx0 + w]
    a = sub[:, :, 3:4] / 255.0 * opacity
    reg = frame[fy0:fy0 + h, fx0:fx0 + w].astype(np.float32)
    frame[fy0:fy0 + h, fx0:fx0 + w] = (sub[:, :, :3] * a + reg * (1 - a)).round().clip(0, 255).astype(np.uint8)
    return frame

def transform(layer, scale=1.0, angle=0.0):
    im = layer
    if scale != 1.0:
        im = im.resize((max(1, int(round(im.width * scale))), max(1, int(round(im.height * scale)))), Image.LANCZOS)
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    return im

def place_center(frame, layer, cx, cy, scale=1.0, angle=0.0, opacity=1.0):
    im = transform(layer, scale, angle)
    return composite(frame, im, cx - im.width / 2, cy - im.height / 2, opacity)

def ease(t, kind='inout'):
    t = min(1.0, max(0.0, t))
    if kind == 'out': return 1 - (1 - t) ** 3
    if kind == 'in': return t ** 3
    if kind == 'back':
        c1 = 1.70158; c3 = c1 + 1
        return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
    return 3 * t * t - 2 * t * t * t
