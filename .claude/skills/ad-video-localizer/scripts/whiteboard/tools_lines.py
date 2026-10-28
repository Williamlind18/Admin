import json, re
def good(w):
    t, c = w[0], w[1]
    if c < 75: return False
    letters = re.sub(r'[^A-Za-z0-9&]', '', t)
    return len(letters) >= 2 or (letters in ('3', '&', 'A', 'I') and c >= 85)
def lines_of(ws):
    ws = sorted([w for w in ws if good(w)], key=lambda w: (w[3], w[2]))
    lines = []
    for w in ws:
        t, c, x, y, ww, hh = w
        cy = y + hh / 2
        for L in lines:
            if abs(L['cy'] - cy) < max(L['h'], hh) * 0.55 and (x - L['x1'] < 1.6 * max(L['h'], hh) and L['x0'] - (x + ww) < 1.6 * max(L['h'], hh)):
                L['w'].append(w); L['x0'] = min(L['x0'], x); L['x1'] = max(L['x1'], x + ww)
                L['y0'] = min(L['y0'], y); L['y1'] = max(L['y1'], y + hh); L['h'] = L['y1'] - L['y0']; L['cy'] = (L['y0'] + L['y1']) / 2
                break
        else:
            lines.append({'w': [w], 'x0': x, 'x1': x + ww, 'y0': y, 'y1': y + hh, 'h': hh, 'cy': cy})
    for L in lines:
        L['w'].sort(key=lambda w: w[2]); L['text'] = ' '.join(w[0] for w in L['w'])
    return sorted(lines, key=lambda L: (L['y0'], L['x0']))
def load(path='ocr/all.jsonl'):
    return {d['n']: d['w'] for d in map(json.loads, open(path))}
