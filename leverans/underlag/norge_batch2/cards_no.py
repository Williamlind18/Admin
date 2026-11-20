"""Norwegian versions of the batch-6 9:16 CTA cards (same layout as v22it/cards.py), from the Nordvask product image."""
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
D = '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/no2/cards/'
FONT = '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/v22it/fonts/Montserrat-ExtraBold.ttf'
W2, H2 = 1440, 2560
def badge(draw, text, cy, size=124, pad=(52, 30)):
    f = ImageFont.truetype(FONT, size)
    l, t, r, b = draw.textbbox((0, 0), text, font=f); w, h = r - l, b - t
    x0 = (W2 - w) // 2 - pad[0]; y0 = cy - h // 2 - pad[1]
    draw.rounded_rectangle([x0, y0, x0 + w + 2 * pad[0], y0 + h + 2 * pad[1]], radius=28, fill='white')
    draw.text(((W2 - w) // 2 - l, cy - h // 2 - t), text, font=f, fill='black')
def card(src, out, badge_text=None):
    im = Image.open(D + src).convert('RGB')
    bg = im.resize((H2, H2), Image.LANCZOS).crop(((H2 - W2) // 2, 0, (H2 - W2) // 2 + W2, H2))
    bg = bg.filter(ImageFilter.GaussianBlur(40)); bg = ImageEnhance.Brightness(bg).enhance(1.04)
    fg = im.resize((1360, 1360), Image.LANCZOS)
    m = Image.new('L', fg.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 1359, 1359], radius=48, fill=255)
    bg.paste(fg, (40, 300), m)
    if badge_text: badge(ImageDraw.Draw(bg), badge_text, 175)
    bg.save(D + out)
def pill(text, out, size=88):
    im = Image.new('RGBA', (W2 // 2, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, size // 2)
    l, t, r, b = d.textbbox((0, 0), text, font=f); w, h = r - l, b - t
    x0 = (W2 // 2 - w) // 2 - 26; y0 = 100 - h // 2 - 16
    d.rounded_rectangle([x0, y0, x0 + w + 52, y0 + h + 32], radius=16, fill='white')
    d.text(((W2 // 2 - w) // 2 - l, 100 - h // 2 - t), text, font=f, fill='black')
    im.save(D + out)
card('p_no.png', 'c1.png')
card('p_no.png', 'c2.png', '50 % RABATT')
card('p_no.png', 'c4.png', '50 % RABATT')
pill('PENGENE TILBAKE I 30 DAGER', 'pill_30.png', 60)
pill('BESTILL NÅ', 'pill_order.png', 96)
