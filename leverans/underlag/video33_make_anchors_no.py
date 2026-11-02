import timeline as T
# (sentence, kind, orig_lo, orig_hi) - Norwegian: enzyme words (offset ~0.7-1.2 s) land on their labels
A = [(10, "start", 41.6, 43.4), (18, "start", 78.0, 79.4), (26, "start", 117.2, 118.4), (28, "start", 125.4, 127.0),
     (30, "start", 133.8, 135.5), (42, "start", 180.4, 181.8), (47, "end", 225.0, 226.2),
     (55, "start", 276.84, 277.24), (57, "start", 287.98, 288.38), (60, "start", 307.85, 308.25),
     (75, "start", 393.6, 394.1), (78, "start", 416.5, 417.2), (82, "start", 437.0, 438.0), (85, "start", 449.15, 450.0)]
print(" ".join(f"--anchor {s}:{k}={T.new(lo):.2f}-{T.new(hi):.2f}" for s, k, lo, hi in A))
