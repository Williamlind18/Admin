#!/usr/bin/env python3
"""White rounded label cards with black Montserrat ExtraBold text, added to a captions.ass file, to cover
foreign graphics in the footage (prices, guarantees, "INVENTED 1904", logos, competitor icons).

Usage: label_cards.py WORK/captions.ass WORK/cards.json --font WORK/fonts/Montserrat-ExtraBold.ttf
cards.json is a list of cards in output time (after any cuts):
  {"t0": 45.85, "t1": 48.3, "x": 130, "y": 45, "w": 460, "h": 420,
   "lines": ["VANLIG TABLETT", "RENGÖR BARA", "*20 %"],      # "*" = big line
   "zoom": 150, "zoom_ms": 450,                              # optional: shrink from 150 % with a zoom-in graphic
   "path": [[0.85, 485], [1.0, 345], [1.8, 100]]}            # optional: x keyframes for a sliding graphic
Plain lines share one size and '*' lines are bigger; text fills the card. Captions move to layer 2 so they
stay on top. Size each card from a gridded frame grid over the graphic's whole lifetime, start it the frame
the graphic appears, and check a 0.1-0.4 s grid of a test render (cards back to back have no fades).
"""
import argparse
import json

from PIL import ImageFont


def ts(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def rrect(w, h, r):
    k = 0.448 * r
    return (f"m {r} 0 l {w - r} 0 b {w - k} 0 {w} {k} {w} {r} l {w} {h - r} b {w} {h - k} {w - k} {h} {w - r} {h} "
            f"l {r} {h} b {k} {h} 0 {h - k} 0 {h - r} l 0 {r} b 0 {k} {k} 0 {r} 0")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ass")
    ap.add_argument("cards")
    ap.add_argument("--font", required=True, help="path to Montserrat-ExtraBold.ttf (for measuring text)")
    a = ap.parse_args()
    cards = json.load(open(a.cards, encoding="utf-8"))

    def width(s, sz):
        return ImageFont.truetype(a.font, max(1, int(sz))).getlength(s)

    def fit(lines, w, h):
        avail, n = w * 0.84, len(lines)

        def biggest(s, cap):
            sz = cap
            while sz > 8 and width(s, sz) > avail:
                sz -= 1
            return sz
        plain = [s for s in lines if not s.startswith("*")]
        star = [s.lstrip("*") for s in lines if s.startswith("*")]
        cap = 0.80 * h / (1.12 * n)
        p_sz = min([biggest(s, cap) for s in plain] or [cap])
        s_sz = min([biggest(s, 0.5 * h) for s in star] or [0])
        sizes = [s_sz if s.startswith("*") else p_sz for s in lines]
        tot = sum(sizes) * 1.12
        if tot > 0.84 * h:
            sizes = [v * 0.84 * h / tot for v in sizes]
        return [int(v) for v in sizes]

    src = open(a.ass, encoding="utf-8").read().replace("Dialogue: 0,", "Dialogue: 2,")
    styles = ("Style: CardBox,Arial,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1\n"
              "Style: CardText,Montserrat ExtraBold,40,&H00000000,&H00000000,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n")
    src = src.replace("\n\n[Events]", "\n" + styles + "\n[Events]", 1)
    ev = []
    for c in cards:
        x, y, w, h = c["x"], c["y"], c["w"], c["h"]
        sizes = fit(c["lines"], w, h)
        txt = "\\N".join(f"{{\\fs{sz}}}{s.lstrip('*')}" for s, sz in zip(c["lines"], sizes))
        box = rrect(w, h, c.get("radius", 24))
        if c.get("path"):
            keys = [tuple(k) for k in c["path"]] + [(c["t1"], c["path"][-1][1])]
            for i, ((ta, xa), (tb, xb)) in enumerate(zip(keys[:-1], keys[1:])):
                if tb - ta < 0.02:
                    continue
                dur, fad = int((tb - ta) * 1000), "\\fad(60,0)" if i == 0 else ""
                ev.append(f"Dialogue: 0,{ts(ta)},{ts(tb)},CardBox,,0,0,0,,{{\\move({xa},{y},{xb},{y},0,{dur}){fad}\\p1}}{box}{{\\p0}}")
                ev.append(f"Dialogue: 1,{ts(ta)},{ts(tb)},CardText,,0,0,0,,"
                          f"{{\\move({xa + w // 2},{y + h // 2},{xb + w // 2},{y + h // 2},0,{dur}){fad}}}{txt}")
        else:
            cx, cy, z = x + w // 2, y + h // 2, c.get("zoom")
            zt = f"\\fscx{z}\\fscy{z}\\t(0,{c.get('zoom_ms', 400)},\\fscx100\\fscy100)" if z else ""
            ev.append(f"Dialogue: 0,{ts(c['t0'])},{ts(c['t1'])},CardBox,,0,0,0,,{{\\an5\\pos({cx},{cy}){zt}\\p1}}{box}{{\\p0}}")
            ev.append(f"Dialogue: 1,{ts(c['t0'])},{ts(c['t1'])},CardText,,0,0,0,,{{\\pos({cx},{cy}){zt}}}{txt}")
        print(f"card {c['t0']:7.2f}-{c['t1']:7.2f} {c['lines']} sizes {sizes}")
    open(a.ass, "w", encoding="utf-8").write(src.rstrip("\n") + "\n" + "\n".join(ev) + "\n")


if __name__ == "__main__":
    main()
