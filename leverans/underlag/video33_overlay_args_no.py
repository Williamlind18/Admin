"""Overlay list for render_ov.py: picture-anchored items in original seconds (mapped through the cuts),
voice-anchored items from words_global.json. Norwegian: no PROTEASE/LIPASE boxes (labels already correct)."""
import json
import timeline as T

G = json.load(open("words_global.json"))
st = {}
for w in G:
    st.setdefault(w["sent"], w["start"])
end = T.duration()
items = [  # (png, orig_start, orig_end)
    ("nasa_a", 223.95, 224.45), ("nasa_b", 224.45, 225.0), ("nasa_c", 225.0, 225.5), ("nasa_d", 225.5, 226.05),
    ("nasa_low", 224.0, 226.05),
    ("amy", 277.6, 279.3),
    ("sms1", 394.75, 395.45), ("sms2", 395.45, 397.45),
    ("card_prod", 416.5, 421.367),
]
spec = [f"ov/{n}.png@{T.new(a):.3f}-{T.new(b):.3f}" for n, a, b in items]
ec = T.new(T.ENDCARD_ORIG)
spec += [f"ov/card_offer.png@{T.new(436.9):.3f}-{st[83] - 0.12:.3f}",
         f"ov/card_years.png@{st[83] - 0.12:.3f}-{st[84] - 0.12:.3f}",
         f"ov/bar_30.png@{st[84] - 0.12:.3f}-{ec:.3f}",
         f"ov/endcard33.png@{ec:.3f}-{end + 1:.3f}"]
print(" ".join(f"--overlay {s}" for s in spec))
