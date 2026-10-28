"""Shared cut list (original seconds) and orig->new time mapping for video33."""
CUTS = [(18.667, 19.367), (28.167, 29.433), (39.333, 41.533), (51.200, 52.733), (57.967, 58.433), (95.267, 97.433), (182.700, 205.967), (255.400, 263.733), (286.700, 287.767), (293.267, 294.267),
        (295.567, 297.467), (324.600, 329.300), (380.667, 381.100), (383.633, 384.133), (412.367, 416.500)]
SRC_DUR = 452.95
ENDCARD_ORIG = 449.333

def new(t):
    s = 0.0
    for a, b in CUTS:
        if t >= b: s += b - a
        elif t > a: return a - s  # inside a cut -> cut point
    return t - s

def duration():
    return new(SRC_DUR)

if __name__ == "__main__":
    print("new duration", round(duration(), 3), "end card at", round(new(ENDCARD_ORIG), 3))
    print("select expr:", "+".join(f"between(t,{a:.3f},{b - 0.001:.3f})" for a, b in CUTS))
