import timeline as T
# (sentence, kind, orig_lo, orig_hi)
A = [(10, "start", 41.6, 43.4), (18, "start", 78.0, 79.4), (26, "start", 117.2, 118.4), (28, "start", 125.9, 127.0),
     (30, "start", 134.3, 135.5), (42, "start", 180.4, 181.8), (47, "end", 225.0, 226.2),
     (55, "start", 277.05, 277.55), (57, "start", 288.2, 288.8), (60, "start", 307.95, 308.45),
     (75, "start", 393.75, 394.35), (78, "start", 416.5, 417.2), (82, "start", 436.9, 437.6), (85, "start", 449.4, 450.0)]
print(" ".join(f"--anchor {s}:{k}={T.new(lo):.2f}-{T.new(hi):.2f}" for s, k, lo, hi in A))
