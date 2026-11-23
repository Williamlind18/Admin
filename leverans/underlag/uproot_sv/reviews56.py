"""Scrolling review screen for video56 (frames 7636-7733): six real reviews from norrtvatt.se's product page
(names, titles and texts verbatim, emojis dropped), in the style of the site's cards. Writes patches/v56_reviews.mp4."""
import sys, os, subprocess, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import font
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = [
 ('Sarah M.', 'Ett måste efter hundbäddarna', 'Efter att ha tvättat hundens bädd brukade jag nästan alltid behöva köra en extra tom tvätt innan jag tvättade våra egna kläder. Testade den här direkt efter hundbäddarna och skillnaden var verkligen märkbar. Framför allt försvann den där kvarvarande lukten i maskinen.'),
 ('Pernilla A.', 'Stor skillnad på vår gamla maskin', 'Vår tvättmaskin är flera år gammal och hade börjat få en lite unken lukt, framför allt runt gummilisten. Efter en rengöring luktade den betydligt fräschare och även handdukarna kändes renare efter tvätt. Väldigt nöjd.'),
 ('Jessica B.', 'Önskar att jag hade hittat dessa tidigare', 'Jag hade aldrig ens tänkt på att själva tvättmaskinen behöver rengöras ordentligt. Vi har en golden retriever som fäller konstant och jag förstår nu hur mycket hår och smuts som faktiskt hamnar i maskinen. Kommer definitivt fortsätta använda dessa.'),
 ('Leif M.', 'Var skeptisk men blev positivt överraskad', 'Trodde helt ärligt inte att en liten tablett skulle göra någon större skillnad. Maskinen såg redan ganska ren ut, men efter rengöringen märkte jag framför allt skillnad på lukten. Tvätten känns mycket fräschare nu.'),
 ('Helena A.', 'Perfekt när man har hund', 'Vi har två hundar och tvättar filtar och hundbäddar hela tiden. Efteråt brukade hela maskinen lukta hund och det låg hår överallt. Efter att ha använt dessa känns maskinen mycket fräschare och framför allt luktar inte nästa tvätt hund längre.'),
 ('Sara M.', 'Äntligen luktar tvätten faktiskt rent', 'Jag trodde länge att det var våra handdukar som var problemet eftersom de kunde lukta lite konstigt även direkt efter tvätt. Testade den här och insåg ganska snabbt att det var själva tvättmaskinen. Stor skillnad redan efter första rengöringen.'),
]
K = 2; W = 720 * K; CW = 664 * K; X0 = (W - CW) // 2
BG = (240, 241, 243); GREEN = (29, 173, 129); INK = (24, 27, 29); GREY = (88, 92, 98)
fn = font('pop_sb', 21 * K); fv = font('pop_r', 15 * K); ft = font('pop_b', 24 * K); fx = font('pop_r', 18.5 * K); fa = font('pop_sb', 22 * K)
def wrap(d, txt, f, w):
    words, lines, cur = txt.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=f) <= w: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur); return lines
def star(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=GREEN)
    import math
    cx, cy, r = x + s / 2, y + s / 2 + s * 0.03, s * 0.36
    pts = [(cx + (r if i % 2 == 0 else r * 0.42) * math.cos(-math.pi / 2 + i * math.pi / 5),
            cy + (r if i % 2 == 0 else r * 0.42) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    d.polygon(pts, fill='white')
def card(name, title, text):
    pad = 26 * K
    tmp = Image.new('RGB', (10, 10)); d = ImageDraw.Draw(tmp)
    lines = wrap(d, text, fx, CW - 2 * pad)
    lh = 27 * K
    h = pad + 50 * K + 18 * K + 26 * K + 16 * K + 34 * K + 8 * K + lh * len(lines) + pad
    im = Image.new('RGBA', (CW, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, CW - 1, h - 1], 18 * K, fill='white')
    y = pad
    r = 25 * K
    d.ellipse([pad, y, pad + 2 * r, y + 2 * r], fill=(226, 229, 233))
    ini = name[0]; tw = d.textlength(ini, font=fa); bb = d.textbbox((0, 0), ini, font=fa)
    d.text((pad + r - tw / 2, y + r - (bb[1] + bb[3]) / 2), ini, font=fa, fill=GREY)
    d.text((pad + 2 * r + 16 * K, y + 2 * K), name, font=fn, fill=INK)
    vx, vy = pad + 2 * r + 16 * K, y + 30 * K
    d.ellipse([vx, vy + 2 * K, vx + 16 * K, vy + 18 * K], fill=GREEN)
    d.line([(vx + 4 * K, vy + 10 * K), (vx + 7 * K, vy + 13 * K), (vx + 12 * K, vy + 6 * K)], fill='white', width=2 * K)
    d.text((vx + 22 * K, vy), 'Verifierad kund', font=fv, fill=GREY)
    y += 50 * K + 18 * K
    for i in range(5): star(d, pad + i * 30 * K, y, 26 * K)
    y += 26 * K + 16 * K
    d.text((pad, y), title, font=ft, fill=INK); y += 34 * K + 8 * K
    for ln in lines:
        d.text((pad, y), ln, font=fx, fill=GREY); y += lh
    return im
cards = [card(*r) for r in REV]
gap = 18 * K
total = sum(c.height for c in cards) + gap * (len(cards) + 1)
sheet = Image.new('RGB', (W, total), BG)
y = gap
for c in cards:
    sh = Image.new('RGBA', (c.width + 40, c.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 24, c.width + 20, c.height + 20], 18 * K, fill=(0, 0, 0, 28))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    sheet.paste(sh, (X0 - 20, y - 20), sh)
    sheet.paste(c, (X0, y), c); y += c.height + gap
print('sheet', sheet.size)
N = 98; H = 900
enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '720x900', '-r', '30', '-i', '-',
                        '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', f'{S}/patches/v56_reviews.mp4'], stdin=subprocess.PIPE)
travel = min(total - H * K / 1.0, 1300 * K)
for k in range(N):
    t = k / (N - 1)
    z = 1.0 + 0.06 * t
    y0 = 40 * K + travel * (0.15 * t + 0.85 * t * t * (3 - 2 * t)) * 0.75
    cw, ch = W / z, H * K / z
    x0 = (W - cw) / 2
    fr = sheet.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((720, 900), Image.LANCZOS)
    enc.stdin.write(np.asarray(fr).tobytes())
enc.stdin.close(); enc.wait(); print('ok', N)
