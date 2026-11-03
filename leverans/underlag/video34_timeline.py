"""Cut list (original seconds) and orig->new mapping for video34 (Uproot packaging shots removed)."""
CUTS = [(15.1, 15.8), (20.3, 20.9), (47.6, 48.3), (87.0, 88.8), (98.0, 98.9)]
SRC_DUR = 108.18
ENDCARD_ORIG = 105.4  # Uproot end image starts here; replaced by our offer card + end card

def new(t):
    s = 0.0
    for a, b in CUTS:
        if t >= b: s += b - a
        elif t > a: return a - s
    return t - s
