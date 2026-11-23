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
  are blocked). The output is voice-only unless the user supplies the music file or asks for one made
  with ElevenLabs Music (see elevenlabs.md). Mix it with `render.py --bed music.mp3 --bed-db -16`.
- With a music bed, render.py's QA counts the music in sentence pauses as "speech without caption"
  (about 1 s on video 5). Re-check coverage on `vo.wav` alone; that must be ~0.00 s.
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
  with the same style and timing rule as make_captions.py. `scripts/chunk_captions.py` does exactly
  this from a `chunks.txt` ("NN: chunk | chunk"), and also draws the label boxes below (video 5).
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
- **Cutting a shot out of the source** (e.g. a competitor's map): find the first and last frame at
  30 fps, cut at a transition (a white flash cuts cleanly), and drop the frames with
  `select='not(between(n,A,B))',setpts=N/FRAME_RATE/TB` (plus the same `aselect` on the audio),
  re-encoded at crf 14. Every anchor after the cut moves earlier by (B-A+1)/fps.
- **Low-resolution sources** (e.g. a 480×832 download): upscale before rendering so the captions are
  sharp. Best free chain, checked on animated footage: `hqdn3d=1.5:1.5:3:3,deband=1thr=0.015:2thr=0.015:
  3thr=0.015:range=12:blur=1,scale=1080:1872:flags=lanczos,cas=strength=0.6`, x264 crf 16, then render
  from that file and build the captions against it. AI upscaling exists but is expensive: Topaz in
  ElevenLabs priced at about 56 600 credits (fast) or 72 000 (precise) for 85 s; Higgsfield cannot
  quote a price in advance. Never run those unasked. Running a downloaded upscaler binary such as
  Real-ESRGAN was blocked by the session's safety classifier.
- **Blurry or empty graphics** (video 15: a "3 REASONS" transition held a smeared panel for 3.5 s): the
  user wants real footage there. Cut the graphic out on its scene cuts and fill the exact frame count with
  footage that fits the line, reused from elsewhere in the ad. Mirror it (`hflip`) so the repeat is less
  obvious, and keep the total length so every later timestamp stays valid.
- **Banners over a montage** (e.g. "15 000+ KUNDER" over customer photos): keep one steady banner for
  the whole montage, from the frame the photos appear to the frame the next shot's subject appears.
  Don't make it follow the counter on and off.
- **Removing burned-in text without a box** (video 15: "60 DAY MONEY BACK" built itself over a 3D
  tablet for 30 frames). Cut the text frames out and fill the gap with the clean frames just before it,
  slowed down with motion interpolation, so the shot keeps its exact length and every later timestamp
  stays valid. Work on PNG sequences, because `select`/`trim` into mp4 drops frames:
  `select='between(n,A,B)' -fps_mode passthrough f/%03d.png`, then
  `setpts=PTS*K,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none` and adjust
  K until the output count is exactly right; splice with `trim=end_frame` + `concat`. Count frames with
  `-vf showinfo` (grep "n:"), not ffmpeg's progress line.
- **Moving labels** (a sign on an animated truck): track the coloured element per frame (colour mask +
  `scipy.ndimage` closing + largest component) and write one label per frame. Use floored centisecond
  times, `start=floor(n/30*100)/100, end=floor((n+1)/30*100)/100`, so consecutive boxes neither overlap
  nor leave a gap, and the last one ends exactly at the scene cut.
- **Short text flashes** inside motion graphics ("3 REASONS" wiping in for 3-35 frames): scan the
  graphic's text band frame by frame; cover each flash with one steady box for its whole span rather
  than many flickering ones.
- **Label text size:** libass renders Montserrat ExtraBold at about half the `\fs` value in cap height
  (`\fs86` gave ~43 px caps). Size labels so text fills ~80 % of the box width: about
  `fs ≈ box_width / (0.41 × characters)`.
- `chunk_captions.py` writes only the ASS file. Get the .srt from `make_captions.py ... --out-dir OTHER_DIR`.
- **Leftover captions of the original** can flash by for a few frames (video 5: "every load," on a white
  paper towel for 0.2 s). Scan the finer frame grids for them and blank them with a text-less label.

## Burned-in captions of the original (video 22)
- **They are the transcript.** The ad had word-synced captions (black text in white rounded boxes,
  centred, y 882-942 of 1280; y 300-360 for the first 9.4 s). `caption_sheets.py` crops that band every
  5 frames, keeps only changed crops and tiles them with times: 327 crops on 4 sheets covered 4:28 and
  gave every line with ~0.2 s timing. The user did not need to paste a transcript.
- **Removing them.** `remove_captions.py` finds the box per frame (white columns around the centre,
  black text inside, mirrored when one side merges with a white background) and fills it with a
  push-pull fill: a blurred patch with no text. It found a box in 7 908 of 8 019 frames; the rest had
  no caption (a 3-frame transition and the end card). It took 8 min on the sandbox.
  - OpenCV Telea inpainting and a top/bottom row blend both left streaks; the push-pull fill looked
    like a soft blur.
  - Check afterwards: a "black text on white" signal (white pixels next to near-black ones) in the band
    fell from a median of ~740 to 0. The few non-zero frames were a black-and-yellow drill, not text.
- **Placing the new captions.** Put them at the box centre (video 22: `--y 0.713`), so the patch sits
  behind them. Where the old captions sat elsewhere (the first 9.4 s at the top), move those Dialogue
  lines with `\pos(540,491)` after `chunk_captions.py`.
- Do the removal on the original resolution, then cut and upscale (720x1280 to 1080x1920 with lanczos
  and `cas=strength=0.5`).

## Cutting the competitor's bundle offer (video 22)
- The original ended with a multi-product bundle (tablets plus washer and dryer sheets) and an end card.
  The user sells only the tablets, so everything about the bundle and every packshot was cut: 205-255 s
  and 260-268 s of the source.
- The new offer and CTA (~22 s of speech) went over neutral shots kept from that stretch: suds in the
  drum, a rubber broom pulling pet hair from a rug, a laundry room, dog hair, a blanket and a woman
  smelling it. They were reordered so that the lines matched them, e.g. "Tre enzymer, gjorda för hem med
  husdjur" over the pet hair on the rug.
- Shots with leftover overlay text (a "making my clothes extra soft" title) and the competitor's own
  box were left out as well.
- Cut and reorder in one ffmpeg pass: `split=N`, then `trim=start_frame=A:end_frame=B+1,setpts=PTS-STARTPTS`
  per shot, then `concat`. Find exact cut frames from frame differences, and confirm the frame count
  afterwards (6 825 = 227.73 s).

## Whiteboard animation with English handwriting (video 29)
- The user asked for the English text in a whiteboard animation to be "written in Swedish" instead.
  `scripts/whiteboard/` does it:
  - OCR every frame (Tesseract) and track each line, predicting pans with global phase correlation,
  - erase the original ink,
  - re-write the line in Patrick Hand in the sampled colour, revealed in step with the hand.

  See its README. About 110 lines were replaced; the coloured ribbons ("AMYLASE" in white on blue)
  needed the MANUAL route.
- Measure the global motion like this (frames A..B, ink made bright, caption band blanked):
  `(dx, dy), resp = cv2.phaseCorrelate(prev, cur, cv2.createHanningWindow((W, H), cv2.CV_32F))` on
  half-size `255 - gray` frames, saved as `motion.json` `{n: [dx*2, dy*2, resp]}`.
- The animation's own captions were black text on white with no box. Inpaint the dark pixels and
  their grey anti-aliased edges in the caption rows (`max < 225`); `remove_captions.py` is for boxed
  captions on footage.
- An on-screen title box and a "BUY 2 GET 2 FREE" offer graphic were replaced too:
  - **Title:** an ASS rounded box in the same colour with Swedish text on top.
  - **Offer:** push-pull fill of the white letters (the background was already defocused), then
    Swedish lines in Montserrat ExtraBold timed to when each original line appeared.
- **Font sizes in ASS vs PIL:** libass draws Montserrat ExtraBold with caps of about 0.5 × `\fs`, PIL with
  about 0.7 × size. Measure widths with PIL at `fs × 0.5 / 0.7`, or ASS text comes out a third too small.
- **Competitor packaging the user does not want shown:**
  - cut the shots of their boxes and the drawn box,
  - blur a defocused box further so its text cannot be read,
  - give packets under a tablet close-up a soft blur below the hand (a feathered ramp, like depth of
    field).
- Swedish ran longer than the dense English voiceover in the animation. The first script needed
  1.2-1.37× there; a 13 % shorter script plus wider anchor windows (±0.5-1 s on lines that only need to
  land on their drawing) brought the peak to 1.066.
- **Shell pitfall:** `until ! pgrep -f "some string"` waiting loops match their own command line and never
  end. Wait on a PID or on an output file instead.

## Norwegian versions of finished ads (videos 14 and 15, 2026-11-02)
- **Same footage, same anchors.** A line-by-line translation (same number of lines) reuses the Swedish
  anchors and label positions unchanged. `leverans/norska/README.md` has the per-video settings.
- **The Norwegian voice is slower.** The user's "Norsk äldre man 55-60 år" read 13.1-13.8 chars/s
  (whole take with pauses) against 15.0 for the Swedish "Äldre man 50-60 år - SE". A straight
  translation of video 15 needed x1.09-1.14, and those three takes (≈7 000 credits) were wasted.
  Before paying for takes in a new voice or language, run `scripts/predict_tempo.py` calibrated on any
  take from that voice. It matched the real takes to about 0.02. Then tighten wording only in the
  blocks that need it (drop "helt", "allerede", "som om den aldri forsvant", and so on), without
  dropping facts or claims. Video 15 came out ~8 % shorter at x1.00-1.01.
- **Takes of the same script vary by up to 6 % in length.** Plan with `--scale 1.03-1.05` and pick the
  take with `score_takes.py`. Also look at the worst per-syllable stretch, not just the count: video 15's
  take C had 42 "drawn-out" words but its worst was 0.57 s/syllable, while take A's was 0.87 s ("to.").
- **Norwegian in the tools:**
  - `language_code: "no"` works for both eleven_v3 and flash v2.5.
  - `align_words.py --lang no` uses espeak `nb`.
  - `make_captions.py --lang no` has a Norwegian function-word list.
  - `make_captions.py --chunks-out chunks.txt` writes the automatic chunks so you can fix them by hand
    and add labels with `chunk_captions.py`.
- **Labels.** Keep the box and fit the word with a PIL width ratio. "GRATIS" at `\fs84` measured 326 px
  against "FRAKT"'s 296 px, so it went in at `\fs76`.
- **Credits ran out mid-batch.** A failed run says "This request exceeds your quota … You have N
  credits remaining". Failed generations are not charged. Tell the user how many credits each
  remaining video needs (≈ 3 takes × characters + 0.55 × characters for the flash reference), and
  leave the flow nodes ready so the next session only has to run them.
- **Setup:** `pip` and `python3` can be different Pythons (pip 3.13, python3 3.11), so every script
  failed with "No module named imageio_ffmpeg". `setup.sh` now uses `python3 -m pip` and checks the
  imports.
- **Changing a node's voice drops its language.** `creative_update_node` with only `voice_id`
  replaced `model_parameters`, so `language_code: "no"` vanished. One take of video 5 was made without
  it (the result lists no "Language" setting). Always pass the full set:
  `model_parameters: {"voice_id": ..., "language_code": "no"}`.
- **A cloned voice can be blocked.** "Voice … may violate our Terms of Service and requires
  verification" means the user must verify it in ElevenLabs. Nothing is charged. Use another of the
  user's voices and tell them.
- **Fast voices leave gaps.** The female "medelålders kvinna - NO" read 18.2 chars/s without pauses, so
  video 5 had 1.9 s gaps before chapter anchors at `--max-gap 0.6`. `--max-gap 0.7` brought them to
  ≤1.2 s. Pick the slower of equally clean takes when there is time to spare.
- **Background ffmpeg:** `ffmpeg -i FILE` with no output exits 1. Under `set -o pipefail` that turned
  `hq_encode.sh` into a silent exit. Also give background ffmpeg `-nostdin`, and never read a
  `.status` file from an earlier run as the result of a new one.

## A voice that barely pauses, free-floating overlay text (video 39, 2026-11-03)
- **Splitting a take without pauses.** "kvinna 30-40 år skånsk - SE" (LzJuwbGODHbc1VvzbMrf) left only
  0.06-0.15 s between sentences, so `split_take.py` marked every row `<-- check` and the ratios swung
  0.58-1.37: the silences could not be told apart. Transcribe each take with Scribe (~5.5 credits/s;
  91 s ≈ 500 credits) and run `split_take.py TAKE SENT --words words.json`. It matches the script to
  Scribe's words (258 of 258) and cuts at the quietest point between sentences, with 0 checks.
- **Scribe doubles as a pronunciation check.** One take came back as "körde vi *in* en" and
  "alfa-*amilas*", another as "tvättmedelshinna" and "Nordtvätt". The take whose transcript matched the
  script word for word was chosen.
- **This voice's length varies a lot between generations.** A 1 700-character measuring take was 109 s
  (15.6 chars/s). The three takes of the final 1 616 characters were 91-94 s (17.2-17.7 chars/s). Plan
  with wide anchor windows. The planner then leaves ~1 s pauses at the topic changes rather than
  speeding anything up.
- **Free-floating white text** (a hook title, a "BUY 2 GET 2 FREE" graphic) has no box for
  `remove_captions.py`. `scripts/remove_overlay_text.py` finds bright, unsaturated pixels in a region
  and frame range, grows the mask over the outline and fills it with the same push-pull fill.
  - `--blur` adds extra blur, e.g. so a defocused competitor box behind the offer can't be read.
  - `--bridge` cross-fades over frames where the text fills the picture. Here that was a 15-frame zoom
    of "money back guarantee". The zoom started 5 frames before the white-pixel count jumped, as
    semi-transparent grey letters. Find the start from the frame-to-frame difference instead.
- **New Swedish overlays in the same places.** Add them as ASS lines on layer 3 after `chunk_captions.py`:
  - the title at `\fs58\bord3.5` at the original's y,
  - the offer at `\fs140` ("KÖP 2", "FÅ 2 GRATIS"),
  - "Fri frakt + 30 dagars / pengarna-tillbaka-garanti" at `\fs72`.

  The original's captions sat higher for 3 s (55.6-58.4 s), so those caption lines were moved to the
  patch with `\pos(540,708)`.
- **Ending without the competitor's box.** The last 5 s were their packshot and end card. They were
  cut, and three result shots from earlier in the ad were reused so the CTA had room: the black water
  draining (for "se vad som kommer ut"), a woman with fresh clothes, and the dog blanket.
- **Shell pitfall:** `cmd1 && cmd2 && (long job) &` sends the whole `&&` chain to the background,
  including variable assignments. Start the background job on its own line.
- **Competitor branding on a tablet wrapper.** "Cleaner Pro" was readable on the wrapper for 1.1 s, while
  the voice said "Men Maskinrent från Norrtvätt klarar det". The wrapper moved too much to blur cleanly,
  so the 34 frames were cut. The line now starts on the bare green tablet. Shift every later anchor
  and overlay by the cut (−1.133 s), and widen the windows around a shot that got shorter.

## Outlined captions all through a 4.5-minute talking-head ad (video 45, 2026-11-03)
- **White captions with a thin black outline and no box** ran under every line, and white things sat in
  the same band (detergent bottles, the washer, white plastic in the drum). Plain white-pixel masking
  would have smeared those. `remove_overlay_text.py --outlined --stroke 13 --grow 5 --min 185` only
  takes white pixels that belong to a thin stroke (they vanish under a 13 px opening) and lie next to
  a dark outline. Tune it first with `--test-frames N,N,... DIR` (before/after PNGs, about 20 s). The
  smudge it leaves is hidden under the Swedish captions, so put them where the old ones were
  (`--y 0.625` here, not 0.75).
- **The competitor's box stood on the washer** in about 75 % of the frames (talking-head layout).
  `--hide-color 30,640,280,980:80-100:0.02:9` blurs its teal pixels' bounding box in every frame
  where they cover at least 2 % of the region. Measure the hue fraction per frame first: the box frames
  gave 0.04-0.08, B-roll gave ~0, so the threshold was clean. Check that the region also covers wider
  shots, where the box sits lower.
- **Other brands in a PiP** (Afresh, OxiClean and Tide packs for 1.6 s while the voice says "alla
  rengöringstabletter i butiken"). They were blurred with an ffmpeg `crop,gblur` + `overlay` limited to
  those frames (`enable='between(n,2169,2216)'`). The same was done for a small competitor box in a
  corner of the ending.
- **Cutting a long video: use `select`, not `split=N` + `trim` + `concat`.** On a 4.6-minute source the
  split branches buffer every frame that has not been consumed yet, and the job was killed for lack of
  memory (exit 137). One `select='not(between(n,A,B)+...)',setpts=N/(30*TB)` pass needs no buffer.
  The ffmpeg here no longer has `-filter_complex_script`. Use `-/filter_complex FILE` instead.
  Do not load all frames as int64 in numpy either (8 312 small frames → 11 GB). Use `mmap_mode='r'`
  and a slice.
- **Planning: few, wide anchors.** 27 anchors (every visual cue) needed up to x1.35. With 9 anchors
  (only the labelled graphics, the cut points and the offer) and windows of 1-2 s, the max tempo was
  x1.046. A label box is timed to its graphic anyway, so the voice may be up to ~1 s off it.
- **Script length.** At 16.3 chars/s the first full translation needed x1.21. Cutting about 17 %
  (repetitions, a second example, "after that I gave it to every pet owner" lines) fitted it at x1.00.
  It held up: the take was 3 818 characters, 235 s of speech.
- **Emojis survive the caption remover.** Blue "⬇️⬇️⬇️" squares under "Link's right down below" stayed after
  the white-text pass and then collided with the new "KÖP 2" overlay. Look at the last 10 s with the
  new overlays on before the final encode. One second of `delogo` (`enable='between(n,A,B)'`) hid them
  under the overlay.
- **`pkill -f PATTERN` kills your own shell** when PATTERN also appears in the command you are running
  (exit 144). List the PIDs with `ps -eo pid,args | grep ...` in one call and `kill PID` in the next.
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
