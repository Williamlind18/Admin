"""SVG seven-segment digits (classic LCD look), drawn as polygons, slanted."""
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg"}

def _seg(name, w, h, t):
    g = t * 0.12
    hx = [(t / 2 + g, 0), (w - t / 2 - g, 0), (w - t - g, t / 2), (t + g, t / 2)]
    def horiz(y):
        return [(t / 2 + g, y), (t + g, y - t / 2), (w - t - g, y - t / 2), (w - t / 2 - g, y), (w - t - g, y + t / 2), (t + g, y + t / 2)]
    def vert(x, y0, y1):
        return [(x, y0 + t / 2 + g), (x + t / 2, y0 + t + g), (x + t / 2, y1 - t - g), (x, y1 - t / 2 - g), (x - t / 2, y1 - t - g), (x - t / 2, y0 + t + g)]
    m = h / 2
    return {"a": horiz(t / 2), "g": horiz(m), "d": horiz(h - t / 2),
            "f": vert(t / 2, 0, m), "b": vert(w - t / 2, 0, m), "e": vert(t / 2, m, h), "c": vert(w - t / 2, m, h)}[name]

def svg(text, dw=120, dh=200, t=26, gap=34, colon=40, slant=0.08, on="#111", off=None, pad=10):
    x = pad; parts = []
    for ch in text:
        if ch == ":":
            cx = x + colon / 2
            for cy in (dh * 0.3, dh * 0.7):
                parts.append(f'<rect x="{cx - t*0.45:.1f}" y="{cy - t*0.45:.1f}" width="{t*0.9:.1f}" height="{t*0.9:.1f}" fill="{on}"/>')
            x += colon + gap * 0.5; continue
        for s in "abcdefg":
            pts = _seg(s, dw, dh, t)
            col = on if s in SEG[ch] else off
            if not col: continue
            p = " ".join(f"{x + px - (py - dh) * slant:.1f},{py + pad:.1f}" for px, py in pts)
            parts.append(f'<polygon points="{p}" fill="{col}"/>')
        x += dw + gap
    W = x + pad + dh * slant
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{dh + 2*pad:.0f}" viewBox="0 0 {W:.0f} {dh + 2*pad:.0f}">{"".join(parts)}</svg>'
