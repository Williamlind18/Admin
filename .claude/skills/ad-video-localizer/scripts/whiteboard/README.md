# Whiteboard animation: replace the hand-written English with Swedish

Made for video 29: a 60 s whiteboard animation where a hand writes about 110 English labels and the
camera pans across panels. Every line is erased and re-written in Swedish in the original colour and
size, in step with the hand. The result passed review frame by frame.

Run everything from the work folder (WORK), with the source at `WORK/dl/src_orig.mp4`. Copy these
scripts there; they import each other and `items.py` from the current folder. Install the tools
with `apt-get install tesseract-ocr`, `pip install pytesseract opencv-python-headless fonttools`.
Put the handwriting font in `WORK/hfonts/` (Patrick Hand from Google Fonts matched the marker capitals;
check that it has å ä ö).

1. **OCR every frame.** Run `OMP_THREAD_LIMIT=1 python3 ocr_all.py FIRST LAST ocr/all.jsonl`. This takes
   about 2.5 min for 1 550 frames on 4 cores. Without `OMP_THREAD_LIMIT=1` the four Tesseract processes
   oversubscribe the CPU and crawl.
2. **List the text.** `tools_lines.lines_of()` groups the words into lines. Print the lines at
   keyframes and write `items.py`, one entry per line:
   - `dict(id, n=keyframe, box=[x0,y0,x1,y1], en=..., sv=..., align='c'|'l')`,
   - plus `bold`, `dy` and `maxw` overrides.
   Translate line by line, so each Swedish line replaces one English line.

   Labels OCR misses, such as small bottle labels and white text on coloured ribbons, go in `MANUAL`
   with `manual=1`. For ribbons, also set `kind='ribbon'`. See `items_video29.py`.
3. **Measure the global motion.** Phase correlation between consecutive frames gives the pans
   (`motion.json`; the snippet is in lessons.md). Pans can move 120 px in one frame. Predicting with the
   global motion is what keeps the tracker on the right line when the same words appear several
   times ("RINSES THIS" ×3).
4. **Track.** Run `python3 track.py`, which follows each item through the OCR words using the motion
   prediction, then `python3 track_manual.py`, which tracks the MANUAL items by motion plus template
   matching. Scale stays fixed at 1, because OCR box heights are too noisy to measure zoom.
5. **Decide when to show each line.** `python3 anim_pass1.py` measures the original ink in every
   frame. A line is shown:
   - while it is detected,
   - for up to 60 frames before that, but only while the camera is still, the ink keeps growing and
     all of it lies on this line (the write-on; the Swedish is revealed left to right by the same
     fraction),
   - for up to 120 frames after it, while at least 60 % of the ink is still there.

   These rules removed every "ghost" line seen in the first tests.
6. **Check, then render.** `python3 anim_test.py 250,600,1254 out.png` renders before/after pairs.
   `anim.render(frame, n, items)` does the real work inside your frame loop:
   - erases the ink (TELEA inpainting),
   - writes the Swedish text, keeping the hand in front.

Sizing that worked:
- **Capital letters:** the font size comes from the cap height of the ink rows. Stretch the text 1.1×
  horizontally, because the marker capitals are wider than Patrick Hand's.
- **Mixed case:** match the width of the English line, and cap the height at 1.2× the line.
- **Pen weight:** add a stroke so the distance-transform stroke width of the Swedish matches the
  original's.
