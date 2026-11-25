"""Danish versions of the batch-6 CTA cards (same layout as the Swedish v22it/cards.py and b6/cards45.py), from the
Nordvask product image. c5 (12 TABLETTER = 1 ÅR) reads the same in Danish and is rebuilt from the same box photo.
usage: cards_da.py CARDDIR   (needs CARDDIR/p_nordvask.png and CARDDIR/p5.png; writes c916/ and c45/)"""
import sys
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
D = sys.argv[1].rstrip('/') + '/'
FONT = '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/v22it/fonts/Montserrat-ExtraBold.ttf'
def build(W2, H2, S, y, bcy, bsize, bpad, out):
    def badge(d, text):
        f = ImageFont.truetype(FONT, bsize)
        l, t, r, b = d.textbbox((0, 0), text, font=f); w, h = r - l, b - t
        x0 = (W2 - w) // 2 - bpad[0]; y0 = bcy - h // 2 - bpad[1]
        d.rounded_rectangle([x0, y0, x0 + w + 2 * bpad[0], y0 + h + 2 * bpad[1]], radius=26 if H2 < 2000 else 28, fill='white')
        d.text(((W2 - w) // 2 - l, bcy - h // 2 - t), text, font=f, fill='black')
    def card(src, name, badge_text=None):
        im = Image.open(D + src).convert('RGB')
        bg = im.resize((H2, H2), Image.LANCZOS).crop(((H2 - W2) // 2, 0, (H2 - W2) // 2 + W2, H2)).filter(ImageFilter.GaussianBlur(40))
        bg = ImageEnhance.Brightness(bg).enhance(1.04)
        fg = im.resize((S, S), Image.LANCZOS)
        m = Image.new('L', fg.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, S - 1, S - 1], radius=48 if S > 1200 else 40, fill=255)
        bg.paste(fg, ((W2 - S) // 2, y), m)
        if badge_text: badge(ImageDraw.Draw(bg), badge_text)
        bg.save(D + out + name)
    def pill(text, name, size):
        im = Image.new('RGBA', (W2 // 2, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        f = ImageFont.truetype(FONT, size // 2); l, t, r, b = d.textbbox((0, 0), text, font=f); w, h = r - l, b - t
        x0 = (W2 // 2 - w) // 2 - 26; y0 = 100 - h // 2 - 16
        d.rounded_rectangle([x0, y0, x0 + w + 52, y0 + h + 32], radius=16, fill='white')
        d.text(((W2 // 2 - w) // 2 - l, 100 - h // 2 - t), text, font=f, fill='black'); im.save(D + out + name)
    card('p_nordvask.png', 'c1.png'); card('p5.png', 'c5.png')
    card('p_nordvask.png', 'c2.png', '50 % RABAT'); card('p_nordvask.png', 'c4.png', '50 % RABAT')
    pill('PENGENE TILBAGE I 30 DAGE', 'pill_30.png', 60); pill('BESTIL NU', 'pill_order.png', 96)
build(1440, 2560, 1360, 300, 175, 124, (52, 30), 'c916/')   # 9:16, as cards_no.py / v22it/cards.py
build(1440, 1824, 1000, 300, 190, 112, (48, 28), 'c45/')    # 4:5, as b6/cards45.py
