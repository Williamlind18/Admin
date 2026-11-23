"""Closing card for the Uproot 1:1 ads (video49/video50): our offer image in place of Uproot's end still.
Layout keeps the caption band (y ~780-860) free because video50's last line runs over the card."""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S0 = '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/'
P = S0 + 'prodimg/'
FD = S0 + 'bf/fonts/Montserrat-%d.ttf'
W, H = 720, 1280
Z = 2
W2, H2 = W * Z, H * Z
BG = (244, 243, 240)
INK = (17, 17, 17)
GREEN = (0, 166, 90)


def F(w, px):
    return ImageFont.truetype(FD % w, round(px))


def text_w(f, t, track=0):
    return sum(f.getlength(ch) for ch in t) + track * (len(t) - 1)


def draw_text(d, x, y, t, f, fill, track=0):
    for ch in t:
        d.text((x, y), ch, font=f, fill=fill)
        x += f.getlength(ch) + track
    return x


def cap_h(f):
    b = f.getbbox('HÄ')
    return b[3] - f.getbbox('H')[1]


class Stack:
    """Vertical list of blocks: (height, draw(img, y_top))."""
    def __init__(self):
        self.items = []

    def add(self, h, fn, gap_after):
        self.items.append((h, fn, gap_after))

    def height(self):
        return sum(h for h, _, _ in self.items) + sum(g for _, _, g in self.items[:-1])

    def render(self, img, top):
        y = top
        for h, fn, g in self.items:
            fn(img, y)
            y += h + g


LOGO = Image.open(S0 + 'bf/logo/logo_raw.png').convert('RGBA')
LOGO = LOGO.crop(LOGO.getbbox())


def wordmark(size):
    """The store's own NORRTVÄTT logo (from the norrtvatt.se header), scaled so its cap height ~ size."""
    w = round(size * 0.74 * LOGO.size[0] / LOGO.size[1])
    h = round(w * LOGO.size[1] / LOGO.size[0])
    lg = LOGO.resize((w, h), Image.LANCZOS)

    def fn(img, y):
        img.alpha_composite(lg, (int((W2 - w) / 2), int(y)))
    return h, fn


def pill(text, size, pad_x=0.75, pad_y=0.55):
    f = F(800, size)
    b = f.getbbox(text)
    tw, th = b[2] - b[0], cap_h(f)
    ph = th + 2 * pad_y * size
    pw = tw + 2 * pad_x * size

    def fn(img, y):
        d = ImageDraw.Draw(img)
        x0 = (W2 - pw) / 2
        d.rounded_rectangle([x0, y, x0 + pw, y + ph], radius=ph * 0.28, fill=INK)
        d.text(((W2 - tw) / 2 - b[0], y + (ph - th) / 2 - f.getbbox('H')[1]), text, font=f, fill='white')
    return ph, fn


def big(text, size, weight=800):
    f = F(weight, size)
    b = f.getbbox(text)
    th = cap_h(f)

    def fn(img, y):
        d = ImageDraw.Draw(img)
        d.text(((W2 - (b[2] - b[0])) / 2 - b[0], y - f.getbbox('H')[1]), text, font=f, fill=INK)
    return th, fn


def check_icon(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
    d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)],
           fill='white', width=max(2, round(r * 0.28)), joint='curve')


def trust_row(parts, size):
    """parts: list of strings; each gets a green check, separated by a thin vertical bar."""
    f = F(700, size)
    th = cap_h(f)
    r = size * 0.5
    gap = size * 0.35
    widths = [2 * r + gap + text_w(f, p) for p in parts]
    sep = size * 1.4
    total = sum(widths) + sep * (len(parts) - 1)

    def fn(img, y):
        d = ImageDraw.Draw(img)
        x = (W2 - total) / 2
        cy = y + th / 2
        for i, p in enumerate(parts):
            check_icon(d, x + r, cy, r)
            d.text((x + 2 * r + gap, y - f.getbbox('H')[1]), p, font=f, fill=INK)
            x += widths[i]
            if i < len(parts) - 1:
                xm = x + sep / 2
                d.line([(xm, cy - th * 0.9), (xm, cy + th * 0.9)], fill=(60, 60, 60), width=max(2, round(size * 0.08)))
                x += sep
    return th, fn


STAR = (245, 171, 0)


def star(d, cx, cy, r):
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=STAR)


def rating_row(size, customers='15 000+ nöjda kunder', score='4,8/5'):
    """'4,8/5 ★★★★★ | 15 000+ nöjda kunder' like the reference's proof line."""
    f = F(700, size)
    th = cap_h(f)
    r = size * 0.52
    sg = size * 0.12
    w_score = text_w(f, score)
    w_stars = 5 * 2 * r + 4 * sg
    w_cust = text_w(f, customers)
    gap = size * 0.4
    sep = size * 1.4
    total = w_score + gap + w_stars + sep + w_cust

    def fn(img, y):
        d = ImageDraw.Draw(img)
        x = (W2 - total) / 2
        cy = y + th / 2
        d.text((x, y - f.getbbox('H')[1]), score, font=f, fill=INK)
        x += w_score + gap
        for i in range(5):
            star(d, x + r, cy, r)
            x += 2 * r + sg
        x += sep / 2 - sg
        d.line([(x, cy - th * 0.9), (x, cy + th * 0.9)], fill=(60, 60, 60), width=max(2, round(size * 0.08)))
        x += sep / 2
        d.text((x, y - f.getbbox('H')[1]), customers, font=f, fill=INK)
    return th, fn


def photo(src, side):
    im = Image.open(P + src).convert('RGB').resize((side, side), Image.LANCZOS)
    m = Image.new('L', (side, side), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, side - 1, side - 1], radius=round(side * 0.06), fill=255)

    def fn(img, y):
        x = (W2 - side) // 2
        sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([x, y + side * 0.03, x + side, y + side * 1.03], radius=side * 0.06,
                                             fill=(0, 0, 0, 60))
        sh = sh.filter(ImageFilter.GaussianBlur(side * 0.035))
        img.alpha_composite(sh)
        img.paste(im, (x, int(y)), m)
    return side, fn



def build(outpath, band=(780, 862)):
    img = Image.new('RGBA', (W2, H2), BG + (255,))
    u = W2 / 2160
    top_parts = [('photo', None, 34 * u * 2), ('wm', wordmark(80 * u * 2), 34 * u * 2),
                 ('pill', pill('KÖP 2  ·  FÅ 2 PÅ KÖPET', 46 * u * 2), 34 * u * 2),
                 ('rate', rating_row(34 * u * 2), 26 * u * 2),
                 ('row', trust_row(['Fri frakt', '30 dagars pengarna tillbaka'], 32 * u * 2), 0)]
    upper_bottom = (band[0] - 30) * Z
    top = 70 * Z
    rest = sum(p[1][0] for p in top_parts if p[1]) + sum(p[2] for p in top_parts)
    side = int(min(0.66 * W2, upper_bottom - top - rest))
    st = Stack()
    for name, blk, g in top_parts:
        if name == 'photo':
            blk = photo('p3.png', side)
        st.add(blk[0], blk[1], g)
    y0 = upper_bottom - st.height()
    st.render(img, y0)
    uh, ufn = big('norrtvatt.se', 74 * u * 2, 700)
    ufn(img, (band[1] + 48) * Z)
    img.convert('RGB').save(outpath)
    print('photo', side / Z, 'content top', y0 / Z, 'url y', band[1] + 48)
if __name__ == '__main__':
    build(sys.argv[1])
