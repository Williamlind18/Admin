# Lessons learned and troubleshooting

## Environment (Claude Code cloud sandbox)
- **ffmpeg:** comes from the `imageio-ffmpeg` wheel (PyPI works). It has **no `drawtext` filter**, so
  all on-screen text goes through ASS subtitles (the `ass` filter, libass) with `fontsdir`.
  Tempo changes use `atempo`. `rubberband` is also installed, but don't use it for voice (see Voice).
- **Reachable:** PyPI, Ubuntu apt (archive.ubuntu.com), Google Fonts, the session's GitHub repo and its
  releases, storage.googleapis.com (ElevenLabs downloads).
- **Blocked:** Hugging Face, OpenAI model CDN, download.pytorch.org, Dropbox, Google Drive,
  WeTransfer, most shop domains, and api.elevenlabs.io unless the user allows it.
- There is no speech recognition, and you cannot listen to audio. Everything about timing comes from
  signal analysis plus the known text. Say so honestly and ask the user to check the result.

## Voice (learned on Maskinrent video 2)
- **One clip per sentence sounds like different people.** eleven_v3 varies timbre, stress and
  pronunciation between calls, and the user heard the joined clips as robotic and uneven. Generate the
  **whole script in one take** and cut it with `split_take.py` instead.
- **rubberband sounds robotic; atempo does not.** In a render the opening 9 s were unstretched
  (tempo 1.00) and the rest sped up 5-8.5 % with rubberband. The user said: "perfect for 9 seconds,
  then it went back to the robotic sound". The same take sped up with `atempo` sounded "so much
  better". `build_voiceover.py` now uses atempo by default.
- A continuous take reads ~4 % faster than per-sentence clips and has clean 0.4-0.8 s sentence pauses,
  so the planner usually needs only 1.00-1.09.
- A re-generated sentence is not guaranteed to be shorter, even with fewer words: a trimmed line came
  back 0.3 s longer. Settle the wording before the take.
- The user's subscription allows 5 concurrent ElevenLabs requests; more fail with "Too many
  concurrent requests" and must be started again.

## Audio
- If the original ad has music under the voice, it cannot be separated here (source-separation models
  are blocked). The output is voice-only unless the user supplies the music file. Mix it with
  `render.py --bed music.mp3 --bed-db -16`.
- **Music from ElevenLabs** (Maskinrent video 3, when the user asked for new music):
  - Add a `music` node with `creative_add_flow_node`, using `eleven_music_v2_5` and model_parameters
    `{"duration_seconds": <video length>, "lyrics_type": "instrumental", "instrumental": true}`.
  - Run it with `creative_run_flow_nodes` and `generations_count: 1`. It cost ≈2 700 credits for 102 s.
  - Describe the sound, not the story: genre, mood, instruments, tempo and how the energy develops.
  - The track came back at about -15 LUFS. Trim it to the video length with a 1-1.5 s fade-out, and mix it
    with `render.py --bed music_bed.wav --bed-db -14`, about 15 dB under the voice.
  - With a bed, render.py's QA line counts the music as speech. Check caption coverage and pauses
    against `vo.wav` instead.
- The loudness target -14 LUFS (`loudnorm`) suits TikTok, Reels and Shorts.
- eleven_v3 speaks about 13 % slower than multilingual_v2, so budget for it.
- With atempo, up to about 1.08× tempo is inaudible. Keep the offer/CTA section at or under about 1.10×.
  Above that, fix the script instead.

## Timing and captions
- The user dislikes long pauses. Use 0.18 s between sentences and cap pauses at 0.45 s. Anchored
  sentences get 0.3 s around them.
- Syncing the ~3 key visual moments matters more than following the original timing everywhere. Anchor
  only those.
- `align_words.py` "spread" column: this is how far the three methods disagree (median, seconds).
  Values ≤ 0.3 s are normal. For sentences with ≥ 0.6 s, look at the chunk timings more carefully in
  the check frames, and mention them to the user as places to double-check.
- Place captions where the old captions were (often blurred bars around 75 % of the height, visible on
  the contact sheets), so the new text covers them. Burned-in original text elsewhere cannot be removed.
  Say so.
- Keep captions to 1-3 words, with no dangling "det / och / ditt" at the end of a chunk. That is already
  handled by make_captions.py. Still read the chunk list: it splits blindly at colons and lists
  ("tre lager: filmen" → "lager filmen"). When several are clumsy, write the chunks by hand, one line
  per sentence with chunks separated by `|`, and build the Dialogue lines from `words_global.json`
  with the same style and timing rule as make_captions.py (Maskinrent video 2 did this).
- **Burned-in foreign text** in the footage (e.g. English labels "FILM / PROTEIN / GREASE" on a close-up):
  the user wanted it covered by **white rounded boxes with black Montserrat ExtraBold text in the
  target language**. Add them as extra ASS events: a `\p1` rounded-rectangle drawing on layer 1 and the
  word on layer 2, with the same start/end. Measure where the text sits over its whole lifetime (it
  may move and flicker). Look at gridded frames every 0.2 s, and size each box to cover the full
  extent plus a margin. End the boxes exactly at the scene cut; find it with frame differences at
  30 fps. Then check a 0.2 s grid of the render to confirm that nothing peeks out.

- **Foreign text on a moving object** (Maskinrent video 3: a "Lipase" label on a bottle that tilts and moves
  while it pours):
  - Track the text in every frame. Mask the white paper, fill its holes, keep the dark ink pixels, and
    take their centroid and PCA angle.
  - Smooth the track over about 5 frames.
  - Write one ASS event per video frame with `\pos`, `\org` and `\frz`. Put the event boundaries
    halfway between frames, floored to centiseconds.
  - End the box once the edge of the frame cuts the word to letters that read the same in Swedish
    ("Lip…").
  - Build ASS lines in a Python file or a quoted heredoc (`<<'EOF'`). An unquoted bash heredoc turns
    `\\an`, `\\frz` and `\\bord` into Python escape characters, and the tags silently stop working.

## Footage and content
- Look for **other brands in the footage** (packaging, websites, logos) and warn the user. Offer to cover
  those shots with the user's product image if they upload one. On Maskinrent video 2 the user chose
  to keep the competitor's box shots.
- When the user sends a re-cut of a video you already did, run `analyze_video.py NEW --reference OLD`.
  Unchanged sections keep their timestamps, so earlier anchors can be reused.
- Rendering 1080×1920 for 110 s takes about 3.5 min on the sandbox. Tell the user it's coming.

## Short ads and end cards (learned on Maskinrent video 3, 30 s)
- **Voices differ in speed.** The voice "30 år kvinna" spoke about 15.3 characters per second, not the
  16.3 that `split_script.py` assumes. The first take (487 characters, estimated ×1.07) needed ×1.14.
  Trimming 36 characters of wording without losing content ("tvättmaskinen" → "maskinen", dropping
  "fortfarande", "De har NASA-klassade enzymer som …" → "NASA-klassade enzymer …") and a new take
  gave ×1.00-1.06. With a voice you haven't measured yet, aim for an estimate of ≤ ×1.00 before the take.
- In a short ad the original's timestamps were almost the same as the scene cuts, and the unanchored
  plan already landed within ~0.3 s of every key visual. One anchor (the NASA line on the microscope/
  astronaut shot) was enough. More anchors pushed single blocks up to ×1.16.
- The original had no price. The user wanted the offer anyway, and a 30 s voice has no room for it, so it
  went on an **end card** instead (`make_endcard.py` + `render.py --overlay`): the product photo, and
  under it a white box saying "HÖSTREA / Upp till 50 % rabatt", from the CTA to the end.
- **Product photo:** the store domain was blocked, and the connected Shopify connector belonged to a
  different store (Hjärtelag SE, not Norrtvätt). Cropping the product photo from the user's screenshot
  (about 520 px, scaled up to about 560 px) looked sharp enough.
- On this video the user said the competitor's box may stay visible, the same as on video 2.

## Removing the original text with Vmake (learned on video25, 20 s)
- The user wanted all burned-in text removed and replaced by their own. Vmake "Smart - Video Smart
  Removal" (SKM0003) removed a large static headline ("UPROOT CLEAN / BUY 2 GET 2 FREE / LAST CHANCE /
  ONLY $9.99/PACK", about the top 40 % of the frame) from a 20 s 720×900 video in about 30 s. One paid run.
- The video came back at 23.93 fps instead of 23.98, 0.1 s shorter, with its own audio (which isn't
  used). Use the cleaned file as the video source and its duration for planning.
- Where the removed text lay over packaging text, that text is smeared. A new headline in the same
  place (`make_text_overlay.py`) hides most of it. Swedish equivalents with the user's real offer:
  "NORRTVÄTT / 2-PACK −40 % / SISTA CHANSEN / ENDAST 25 KR/TABLETT".
- The script for a 20 s ad came out at 15.4 s of speech with "kvinna energisk - SE", so the voice ends
  about 2.7 s before the video. Pauses are capped at 0.45 s. The alternative is a spoken CTA line, which
  needs a new whole take.
- A release that is only a draft can't be fetched from github.com/…/releases/download (404) or with the
  built-in `gh api` (it refuses the redirect). `curl -L -H "Accept: application/octet-stream"
  https://api.github.com/repos/OWNER/REPO/releases/assets/ASSET_ID` works. Find ASSET_ID with
  `gh api repos/OWNER/REPO/releases`, which also lists drafts.
- Check that the uploaded video matches the script before paying for anything. Video24 was a 3:43 ad
  that had nothing to do with the 20 s transcript. The right file was video25.

## A 4-minute ad with everything replaced (learned on video30)
- **No script from the user.** Scribe transcribed the original with word times (1,136 words, 243 s).
  The Swedish script had to be condensed to about 60 % (3,941 characters) to fit, while every story
  step was kept. One eleven_v3 take of all 3,941 characters worked; check it first with `estimate_only`.
- **The voice "Äldre man 50-60 år - SE" pauses only 0.12-0.33 s between sentences.** `split_take.py`
  marked almost every row `<-- check`, but the ratios were 0.7-1.26 and the alignment spreads were
  mostly ≤ 0.3 s, so the cuts were right. Check the ratios and spreads before regenerating anything.
- **Anchors.** Fifteen anchors pushed blocks to ×1.15-1.17. Seven anchors with ±2 s windows gave at
  most ×1.06. Adding anchors can raise the tempo of *earlier* blocks. Labels that appear a couple of
  seconds before the voice names them (the enzyme names) are fine.
- **What Vmake (SKM0003) left behind on a long video:**
  - It removed the plain captions and most of the flat labels.
  - It did not remove glowing or stylised price text ("GET 2 FREE", "$9.99 per box"), badges (one
    was removed but left a gray smear, the other stayed), or labels printed on 3D objects ("Alpha
    Amylase", "Protease", "Lipase").
  - It damaged an icon in an animated graphic.
  - It turned 6.6 s of black frames at the end into noise. Trim the end or cover it with an end card.
  - Always scan the cleaned video at 1 fps before building overlays.
- **Fixes that worked:**
  - White boxes with black text over the leftover text, timed to the exact shot cuts (found with frame
    differences).
  - Swedish badges with claims from the user's page ("AVKALKAR", "PASSAR ALLA TVÄTTMASKINER") in place
    of claims we don't make (EWG, septic safe).
  - Redrawn check marks.
  - For the animated "PET HAIR = PROTEIN / SEBUM = FAT" graphic, the original footage was spliced back
    in for those 1.7 s. Only the words that differ in Swedish were covered, with paper-texture patches
    copied from the same frame: DJURHÅR and FETT.
- **The user asked to remove the competitor's end image** and to make their own from the product page:
  a full-screen end card with the stars and customer count, NORRTVÄTT, the product photo, HÖSTREA,
  "4 PAKET –50 % · FRI FRAKT", a "SÄKRA ERBJUDANDET" button and the 30-day guarantee. Leave free space
  at y ≈ 0.75 for the captions.
- **Claims were adapted to the page:**
  - "Over two million pet owners" became "+15 000 kunder".
  - "Buy 2 get 2 free" became "4 paket till halva priset" (the 4-pack is 50 %).
  - "$9.99/box" became "20 kr per tablett".
  - The 60-day guarantee became the 30-day one.
  - "One tablet every two weeks" became "en tablett i månaden", since 12 tablets last a year.
  - The competitor's customer stories became generic advice, plus the real review from the page
    (Erika, two dogs).
  - Brand names (Afresh, OxiClean, Tide) became "vanliga maskinrengörare".
- Rendering 247 s at 720×1280 with 14 overlays and music took about 7 min, and splicing the source
  took 2 min. The full-quality file was 78 MB at crf 22, under GitHub's 100 MB limit.

### Round 2 of video30: what the user wanted changed
- **Enzyme names had to be spoken exactly when their labelled 3D shots appear.** The voice was 3 s
  late. The fix was a shorter script before each enzyme (−52 characters across s37-s45) and tight
  anchors (`42:start=142.2-142.6`, `44:start=150.7-151.1`, `47:start=162.85-163.2`). The result was at
  most ×1.044. Labels that appear before the voice names them are **not** fine for this user.
- **Offer boxes must not cover the product packaging,** and nothing may sit outside the Meta 4:5 crop
  (the 30-day box at y 0.83-0.93 was too low). The stylised English price text that sat on the
  packaging ("GET 2 FREE", "$9.99 per box") could not be removed:
  - a second SKM0003 pass changed nothing,
  - SKM0005 "Smart Pro" needs a Vmake Pro membership (`membership_required`, no charge).

  Those two shots (3 s and 2.4 s) were replaced with offer cards showing the user's own product photo,
  a slow zoom made with `zoompan`, and the offer text above and below the product. They were spliced in
  with `overlay … enable=between(t,…)` on the source.
- **"Höstrea" became "rea som snart avslutas"**, which needed a new whole take. The first new take
  came out 10 % slower (312 s with long pauses, 258 s of speech) and didn't fit. A second take of the
  same text took 239 s. That take had 0.10-0.16 s sentence pauses, and the pause-based split put
  sentences 55 and 59-61 wrong (ratio 1.34 and 0.69).
- **Cutting by Scribe word times worked:** `split_take.py --words` matched 672 of 679 words, and every
  sentence came out right with spreads ≤ 0.63 s. Scribe cost 1,360 credits for 239 s.
- With a music bed, render.py's QA now measures speech on the voice track (the music had counted as
  4.5 s of "speech without caption").

## A 7-minute ad in paragraph takes (learned on video33, 453 s → 399 s)
- **Twelve eleven_v4 paragraph takes (6 480 characters) read about 16 characters/s**, so the voice was
  ~25 s shorter than the footage. Slowing it to ×0.95 *and* stretching pauses to 0.4 s still left
  0.6-3 s gaps before anchors. **Trimming B-roll fixed it:** removing ~16 s of redundant or competitor
  shots (Affresh/Tide packs, a second "fabric softener" shot) gave ×0.95-1.03 with 0.2 s pauses. Cut
  whole shots at frame-exact scene changes (frame differences around the analysis cut times).
- **`split_takes.py` picked comma pauses in 3 of 12 takes** (colon/comma pauses of 0.3-0.45 s are as
  long as sentence ends in v4). Connect a speech-to-text node (`eleven_scribe_v1`) to each TTS node
  in the same flow (no upload needed; 0 credits in this workspace in Oct 2026). Then run
  `scripts/cuts_from_words.py TAKE.mp3 WORDS.json SENT_DIR ids…` and pass its output to
  `split_takes.py --cuts`. The cut goes in the quietest stretch between the last word of one sentence
  and the first of the next.
- **align_words.py was up to 1 s off in a few sentences** (a long first word such as
  "Huskykvinnan"). Mapping the Scribe word starts into each tightened clip (take time − cut, minus the
  pauses tighten_pauses removed) and replacing words that differ by > 0.25 s fixed it.
- **burned_captions.py remove left captions on screen in two cases:**
  - detection gaps where the caption text changes (the gap is only held when the boxes before and
    after match),
  - captions on a white background (e.g. a washer lid), which are never detected.

  OCR the cleaned video (tesseract, every 0.5 s, only the kept parts) and re-clean those frames with
  the union of the boxes before and after the gap, plus manual boxes.
- **Pitch check with pyin:** for a deep male voice use `fmax ≈ 190`. With fmax 300 pyin jumped an
  octave and flagged half the clips.
- **Text message on screen:** a Swedish bubble in the same place, colour and size, with a short typing
  stage first. The captions move below it (`\pos` y 1000) while it is shown.
- **Full-screen cards** (product name, offer, "räcker i 4 år", end card) keep y 825-890 free for the
  captions at y 0.67, and keep everything inside y 190-1090.

## Re-making a finished ad in another language (learned on Norwegian video30/33, 2026-11-02)
- **The scratchpad from the first version may be gone.** Overlay times and splices can be recovered from
  the delivered file: align it to the source with tiny grayscale thumbnails (36×64, a DP over a
  non-decreasing frame offset finds the cuts), then diff it per overlay box against the new Vmake-cleaned
  video (144×256, mean abs diff > 12) to get each box's on/off times to the frame. Sentence starts come
  from the delivered .srt (match its chunks to the script word by word) and work directly as anchors,
  because the translated script keeps one line per original line.
- **Enzyme words move inside the sentence in another language** ("Det første, alfa-amylase" puts the
  name ~0.7-1.2 s in). Shift the start anchor by the word's offset in `fused.json` so the name lands on
  the label.
- **ffmpeg splice pitfall:** `-ss T -t D -itsoffset T -i src.mp4` did *not* overlay at T (the shot stayed
  the cleaned one). When the source shares the timeline, overlay the whole source input with
  `enable='between(t,a,b)'` instead, and check a frame inside the splice.
- Reusing the earlier music generation (`creative_get_flow_node` → `creative_get_generations`) costs nothing.

## Small caption boxes that move between two heights (learned on video34, 2026-11-03)
- `burned_captions.py detect` missed most of them (boxes ~36 px high at y≈409 *and* y≈817, sometimes a
  two-line box at 355). Two scripts in `scripts/` worked instead:
  - `ocr_boxes.py VIDEO OUT.json 5` finds white boxes (closing fills the text) and OCRs them with
    tesseract (`apt-get install tesseract-ocr`) to read the original script with times. **Set
    `OMP_THREAD_LIMIT=1`** (the script does): with 4 parallel calls tesseract took ~50 s per crop instead
    of 0.2 s.
  - `find_boxes.py VIDEO OUT.json` lists the centred caption boxes in every frame for the inpaint.
- **Gap filling across a scene cut smudged a face:** a top-band box from the next shot was painted over a
  woman's eyes while her caption sat at the bottom. Only apply filled/neighbour boxes where the frame
  really shows a white box there (`min(RGB) > 200` on more than 45 % of it), plus hand-checked manual
  boxes. Then re-run `find_boxes.py`/`ocr_boxes.py` on the cleaned video: nothing readable should remain
  outside the shots that get covered by cards.
- **Trimming for a shorter voice:** cut the tails of B-roll shots at scene cuts (0.6-0.9 s each) where
  the planner leaves gaps > 0.4 s.
- **The user does NOT want our product cards laid over the competitor's clips** (2026-11-03: "du har lagt in
  en bild vid varje videosnutt uproot syntes, så ska det inte vara"). Keep the original clips, packaging
  included, and replace only the competitor's still image at the very end with our end card. If the
  original has no end still, add none.

## A 4-minute Uproot ad with captions in three bands (learned on video43, 2026-11-03)
- Neither `find_boxes.py` nor `ocr_boxes.py` found every caption (white boxes merge with bright footage):
  whole captions survived the first clean. What worked: treat captions as continuous (each one stays until
  the next appears) and mask each OCR'd box from its first sample to the next caption; then list the spans
  that no detected or manual box covers and mask them with a wide band box (here x 84-636, y 792-852).
  The Swedish captions at y 0.645 sit on that band and hide most of the smudge.
- Check the cleaned video with a 1 fps contact sheet of the caption bands, not only OCR: OCR missed
  fully visible leftovers twice.
- Trimming 20.7 s of B-roll (tails of shots at scene cuts, plus a map that said "Florida" and a badge shot)
  brought a 251 s original to 230 s for 201 s of Swedish speech, with tempo ×0.95-1.05 and pauses ≤ 0.5 s.
- ElevenLabs Music (140 s, instrumental) cost 2 100 credits although the estimate said 4 242.

- **Long videos (5 min, Maskinrent video 4):**
  - Rendering takes about 10-12 min.
  - At CRF 21 the full-quality mp4 is far over GitHub's 100 MB limit per file. Re-encode it for the
    repo with a two-pass bitrate target of about 95 MB, from the source with the same ASS filter.
  - render.py's chat preview gets only ~0.5 Mb/s at 1080p for 5 min. Make the preview at 720p
    instead.
  - Full-length music costs about 26.5 credits per second (≈8 300 for 313 s). Offer a ~100 s loop as
    the cheaper option.
- **Highlighted lines on a moving label** (an ingredient list with a marker sweep): track the coloured
  highlight. The centroid moves while the highlight sweeps, so compute the line's y at the box centre
  from the centroid and the angle: `y = cy + (cx - x_box) * tan(angle)`. Fit the band of a static,
  tilted highlight with a least-squares line through its pixels. Eyeballed angles were 3° off, and the
  box missed by half a line.

## Removing burned-in captions and translating on-screen text (Maskinrent video 7)
The user asked to remove the original captions themselves, so no script was supplied.
- **Script with timestamps from the captions.** `scripts/ocr_captions.py SRC OUT` finds the white
  caption box in every frame, groups frames into captions and reads each once with tesseract. The
  result is the English script with exact times, and it also writes per-frame mask rectangles.
  Fix obvious OCR slips by hand (`l` / `|` for `I`).
- **Removing text: LaMa, not OpenCV.** OpenCV `inpaint` and xphoto FSR leave smeared bands on
  anything but flat floors. LaMa (`scripts/lama_inpaint.py`, model from the simple-lama-inpainting
  GitHub release) fills them invisibly. The auto-mode classifier blocks loading the downloaded
  TorchScript model until the user allows it, so ask first. On the 4-core sandbox it does
  ~0.7 s per frame (1.8 s with two parallel processes): a 5-minute video took ~2 h, so start it
  early, run it in the background and do the other steps meanwhile.
- **Big coloured headline texts** (enzyme names, offers): measure each text's box and frame range
  from colour masks, remove it with LaMa, and draw the Swedish text in the same place: Montserrat
  Black, vertical colour gradient, dark rim and soft drop shadow, with a short pop-in.
  Time offer texts to the words in the new voice (`words_global.json`), not to the original frames,
  when a cut has shifted the rhythm.
- **Facebook posts and comments in the footage:** rebuild each view in Swedish with Swedish names
  (Inter 400/600 at the measured size, ~16.9 px for post text at 720 px width), copy avatars and
  emoji from the frame, keep blurred product names blurred, animate highlighter sweeps like the
  original. Track every screenshot with SIFT + RANSAC homographies against a reference frame and
  warp the overlay per frame (premultiplied alpha). For fast zooms where SIFT fails, multi-scale
  template matching against the reference finds the crop. Clip overlays to the white card
  during scroll transitions.
- **Cut sections** (the competitor's trade fair, their end card): find the exact frames from
  frame differences, drop them in the frame loop and cut the old captions mask the same way.
- **Voice longer than the footage after cuts:** slowing the footage by 6 % (re-timed to
  30/1.06 fps, no frame blending) was invisible and kept the voice at ≤ 1.07 tempo with all key
  moments within ~1 s.

## Translating a finished ad into another language (Norwegian versions of Maskinrent 3-6)
The user wanted the same ads "exactly the same, only in Norwegian" (same footage, offer in NOK,
brand and product renamed, a male voice where the Swedish one was male and a female voice where it
was female).
- **Reuse the delivered timing.** The Swedish .srt already holds the approved timing. Every SRT
  entry belongs to one sentence, and a sentence ends at an entry ending in `.`, `?` or `!`. Parse the
  sentence starts, translate line by line (1:1 sentences) and anchor the new sentences around those
  starts with `optimize_anchors.py` + `plan_timeline.py` (every 3rd-5th sentence, ±1.5-2.5 s).
- **When the translation is much shorter** (Norwegian was 22 % shorter on video 6), anchors leave
  0.7-2.5 s holes. Use `plan_timeline.py --min-tempo 0.92` or a least-squares plan with even gaps
  and a mild slow-down (video 6: tempo 0.92, pauses ~0.8 s). Always pin the first sentence to
  ~0.15 s: a free optimizer once started the voice 2.1 s in, a silent hook.
- **Voice rates differ a lot between Norwegian voices** (12-18 characters per second). Test a short
  paragraph with each candidate before the full take. Some library voices are blocked ("may violate
  our Terms of Service and requires verification"): pick another one.
- **Labels from the old render.** Diff the delivered render against the source at half resolution
  and keep white, nearly filled boxes. That gives every label's geometry per frame (minAreaRect),
  so the new-language label goes in the same box: one ASS event per frame, `\frz` from the box angle,
  times floored to centiseconds. Drop labels whose original text is already correct in the new
  language (e.g. "Lipase").
- **Music level.** Least-squares fit the original music track against the delivered mix (5 s blocks)
  to get the voice-over-music ratio the user approved, then choose `--bed-db` so the new voice track
  has the same ratio. On Maskinrent 4 the music sat only ~9 dB under the voice, not 15.
- **Captions:** Norwegian function words are in `make_captions.py --lang no`. Show money and counts as
  digits ("999 kroner", "30 dager", "15 000"); keep the number phrase together in the .srt too.

## Danish versions of the seven Swedish winners (Nordvask Maskinren, November 2026)
- **Check the source against Meta first.** Download the live video (`download_hd_url`) and compare it with the
  GitHub source at 2 fps plus the audio envelope. b1 C3 matched in picture but the live one had a music bed that
  our file lacked: extract it as `live − H(f)·ours` per frequency bin in 8 s blocks (STFT), then a Wiener-style
  mask against the leftover voice. That left the old voice ~32 dB under the voice level, masked by the new voice.
- **Burned-in text: Vmake `SKM0002` (remove subtitles)** keeps fps and length and is clean on captions. It also
  wipes text inside white label boxes but can leave the empty box (FÖRE/EFTER on b5 C2). Scan for white boxes whose
  dark text disappeared between source and clean (`find_labels`-style diff) and put the new-language label in the
  same box. Product cards with the Swedish brand are not removed: replace them with the local brand's product image.
- **Paragraph takes on eleven_v4 barely pause between some sentences.** `split_takes.py` (vowel-proportional
  guess) put ~16 of 49 boundaries on comma pauses. `scripts/espeak_cuts.py` (DTW against an espeak-ng reading of
  the same sentences, snapped to real silences) matched the ElevenLabs Scribe word times on every checked boundary;
  feed its cuts to `split_takes.py --cuts`. Scribe (`creative_transcribe_audio`, 0 credits) gives word times, but
  they run ~0.15-0.3 s late and every status call dumps all words into the context, so use it only to verify.
- **Timing:** `scripts/plan_on_reference.py` puts each sentence near the original sentence start (from the .srt),
  with tempo 0.92-1.08 and pauses 0.2-1.2 s. Danish ran 5-23 % shorter than Swedish; c8 needed 0.92 and ~0.8 s
  pauses, and where the Swedish voice itself was slow (one sentence 9 s vs 6 s) let the pauses there grow rather
  than drift 2 s off the footage.
- **Loudness:** Danish v4 voices peak higher than the Swedish deliveries, so scaling to the Swedish RMS clips.
  Mix voice + bed at the Swedish voice/music ratio, then two-pass `loudnorm` to the Swedish ad's integrated loudness
  (≈ −15 LUFS, TP −1.5).
- **Captions:** `make_captions.py --lang da`. Merge "den/det/de her" into one token, don't end a chunk on a bare
  number word, and show money, percentages and counts ≥ 10 as digits ("999 kroner", "50 %", "15.000 kunder").

## Long competitor ads with hooks (Maskinrent videos 8-10, Uproot footage 720x1280)
- **Small or merged caption boxes:** `ocr_captions.py --mode bands --band 0.15-0.75 --box-h 0.018-0.05`.
  Bands mode can find the box a few rows short, and LaMa then leaves its top or bottom edge as a thin
  white line (22 % of the frames on video 10). Pad the masks by about 12 rows (`--vpad 12`). Afterwards,
  scan the cleaned video for bright rows just outside each old mask, and re-inpaint only those frames
  with a taller mask. On video 10 that cut 1 459 frames down to 0 real remnants in about 15 min.
- **Karaoke hooks** (big white uppercase words with a red box behind the word being spoken): remove
  them with a fixed rectangle over the hook frames. Rebuild them in Swedish from the voice's word
  times: Montserrat ExtraBold at ~62 px on 720 px width, a 3 px black rim, a red (#E40001) rounded box
  with ~20 px padding, and 2-word groups. Measure each word's x-range by rendering it with libass in a
  marker colour, not with PIL, so the box lines up with what libass draws.
- **Different voices, very different speeds:** "äldre kvinna 60+ - SE" read one script at ~15 characters
  per second and the next at ~12, a 63 s take for a 53 s video. "Äldre man 50-60 år - SE" reads at
  ~15.2. Run a short rate test (about 220 credits) before a long take. When a take is far too long,
  tighten the wording, keep every point, and take it again.
- **Takes with uneven pauses:** use `split_take_ref.py`. When a cut lands in a dip instead of a pause,
  compare the neighbouring lengths with espeak estimates. Recut by hand at the real pause if both
  sentences get closer to their estimate.
- **Uneven slack:** when the translation is shorter in one half and longer in the other, run
  `optimize_anchors.py` with windows that are wider on the early side (about -3.5 to +1 s). Slack then
  moves forward and the speed-up stays at or under 1.08, at the cost of 2-3 s of drift around the
  middle.

## Lip sync for AI presenters (video46 test, not produced)
The user asked whether an AI presenter talking to camera could speak Swedish. The ElevenLabs connector
offers several video-to-video lip-sync models. Each takes a `video` and an `audio` port; `sync_mode`
defaults to cut_off.
- **Getting files in:** `creative_attach_reference_file` needs a direct https URL. A clip and a voice
  wav pushed to the public repo and fetched via raw.githubusercontent.com worked.
- **Price per 10 s, measured with `estimate_only`:**

  | Model | Credits per 10 s | Result |
  |---|---|---|
  | `veed-lipsync` | ~410 | The user found it "not good at all". |
  | `veed-lipsync-v2` | ~4 250 | Not tested. |
  | `sync-lipsync-v2-pro` | ~5 060 | Not tested. |
  | `sync-lipsync-v3` | ~8 100 | "Pretty good, not perfect but enough". Colours stay closer to the source than Veed's. |

- **The price depends only on duration.** A 360×360 crop of the face cost exactly the same as the
  full 720×1280 frame.
- **Measure the presenter's screen time first.** Count face-visible seconds with a Haar cascade at
  2 fps (download `haarcascade_frontalface_default.xml` from the opencv GitHub repo; the pip wheel
  ships without it). Price it before proposing anything: a 4:37 ad with the presenter on screen for
  238 s would have cost ~190 000 credits with Sync 3, and the user dropped it. Offer a 45-75 s cut
  instead.
