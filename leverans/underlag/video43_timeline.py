"""Cut list (original seconds) and orig->new mapping for video43."""
CUTS = [(27.1, 27.9), (30.0, 30.9), (41.0, 43.0), (45.5, 46.5), (49.8, 50.7), (70.5, 71.4), (95.2, 97.2), (117.6, 118.6), (126.6, 128.0), (144.8, 145.8),
        (155.3, 159.1), (188.1, 190.5), (239.8, 242.4)]
SRC_DUR = 251.31
ENDCARD_ORIG = 248.2

def new(t):
    s = 0.0
    for a, b in CUTS:
        if t >= b: s += b - a
        elif t > a: return a - s
    return t - s
