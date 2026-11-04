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
