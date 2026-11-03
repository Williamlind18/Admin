# Lessons learned and troubleshooting

## Environment (Claude Code cloud sandbox)
- **ffmpeg:** comes from the `imageio-ffmpeg` wheel (PyPI works). It has **no `drawtext` filter**, so
  all on-screen text goes through ASS subtitles (the `ass` filter, libass) with `fontsdir`.
  Tempo changes use `atempo`. `rubberband` is also installed, but don't use it for voice (see Audio).
- **Reachable:** PyPI, Ubuntu apt (archive.ubuntu.com), Google Fonts, the session's GitHub repo and its
  releases, storage.googleapis.com (ElevenLabs downloads).
- **Blocked:** Hugging Face, OpenAI model CDN, download.pytorch.org, Dropbox, Google Drive,
  WeTransfer, most shop domains, and api.elevenlabs.io unless the user allows it.
- There is no speech recognition, and you cannot listen to audio. Everything about timing comes from
  signal analysis plus the known text. Say so honestly and ask the user to check the result.

## Audio
- **rubberband sounds robotic; atempo does not** (another session, Maskinrent video 2 with eleven_v3).
  The opening 9 s were unstretched and the rest sped up 5-8.5 % with rubberband. The user said: "perfect
  for 9 seconds, then it went back to the robotic sound". The same take with `atempo` sounded "so much
  better", so `build_voiceover.py` uses atempo by default. (Video31 used rubberband at only 0.95-1.05 and
  sounded fine, but keep atempo.)
- The connector exposes **no voice settings** (stability, seed, similarity, speed) for eleven_v3 or
  multilingual_v2. The schema only has `voice_id` and `language_code`. Consistency has to come from
  how the audio is generated: paragraph takes (v4) or one whole-script take (v3, `split_take.py`).
- A regenerated sentence is not guaranteed to be shorter, even with fewer words: a trimmed line came back
  0.3 s longer. Settle the wording before generating.
- If the original ad has music under the voice, it cannot be separated here (source-separation models
  are blocked). The output is voice-only unless the user supplies the music file. Mix it with
  `render.py --bed music.mp3 --bed-db -16`.
- The loudness target -14 LUFS (`loudnorm`) suits TikTok, Reels and Shorts.
- eleven_v3 speaks about 13 % slower than multilingual_v2, so budget for it.
- Sentence-by-sentence generation (video 2, first version) made the voice uneven: pitch per clip varied
  95-157 Hz for a ~110 Hz voice, stress and pronunciation changed, and one clip came out as a female
  voice. The user heard it as "two different people" and "a bit robotic". Paragraph takes with
  `language_code: "sv"` fixed it (pitch spread 35 Hz → 12 Hz with v3). See `references/elevenlabs.md`.
- In paragraph takes eleven_v3 reads ~8 % slower than its single sentences, and eleven_v4 ~15 % faster
  than v3. The user preferred v4 ("much more human, natural speed") but heard a slight echo; its word
  tails ring ~20 ms longer than v3's. A gate or expander in ffmpeg does not measurably help. The
  ElevenLabs Voice Isolator is made for this (~1 000 credits per minute), so offer it rather than run it.
- Do not speed a slow take up past ~1.08 to make it fit: the user hears it as robotic. Pick a faster
  model, trim the script with the user's consent, or let `plan_timeline.py --min-tempo` absorb spare
  time when the voice is shorter than the video.
- Up to about 1.08× tempo is inaudible. About 1.11× is fine for an offer or call-to-action section.
  Above about 1.13× it starts to sound rushed, so fix the script instead.

## Timing and captions
- The user dislikes long pauses. Use 0.18 s between sentences and cap pauses at 0.45 s. Anchored
  sentences get 0.3 s around them.
- Syncing the ~3 key visual moments matters more than following the original timing everywhere. Anchor
  only those.
- Long videos (~5 min) with many key visuals: `plan_timeline.py` handles 20+ anchors. Above ~150 000
  window combinations it switches to a chain search that is exact for the maximum tempo, so it no longer
  coarsens the windows. Give each anchor a window of about 1-2 s and drop anchors whose line cannot fit
  (e.g. a line pinned between two anchors only 3 s apart).
- A fast English voiceover (~20-27 characters/s) needs the Swedish script about 25 % shorter to fit the
  same cut. Merge repeated points instead of dropping beats. Speaking rates differ per voice ("Äldre man 1"
  ran at ~15.5 characters/s), so generate a few sentences first, measure them with `align_words.py`, and
  trim the rest before generating everything.
- `align_words.py` "spread" column: this is how far the three methods disagree (median, seconds).
  Values ≤ 0.3 s are normal. For sentences with ≥ 0.6 s, look at the chunk timings more carefully in
  the check frames, and mention them to the user as places to double-check.
- Place captions where the old captions were (often blurred bars around 75 % of the height, visible on
  the contact sheets), so the new text covers them. Burned-in original text elsewhere cannot be removed.
  Say so.
- Keep captions to 1-3 words, with no dangling "och / i / ett" at the end of a chunk. make_captions.py
  splits each phrase with a small search that penalises such endings and lone short words (strict 3-word limit).
  Still read the chunk list. If several chunks are clumsy, write them by hand in `WORK/chunks.txt`, one line
  per sentence with chunks separated by `|` (`12: Det bor noe | i vaskemaskinen din | akkurat nå`), and pass
  `--chunks WORK/chunks.txt`; the other sentences keep the automatic split. A colon also ends a phrase.
  The Norwegian video2 needed 37 of 73 sentences by hand (verb-subject order like "vet jeg", "grand danois").
- The .srt holds one subtitle per sentence on up to two lines of about 42 characters, split evenly (a cut
  after a comma is preferred); sentences over ~84 characters become several subtitles. The old rule
  (start a new subtitle at 42 characters) left orphans like a lone "nå." for 0.3 s.
- **Burned-in foreign text in the picture** (e.g. English labels "FILM / PROTEIN / GREASE" on a close-up):
  the user wanted it covered by **white rounded boxes with black Montserrat ExtraBold text in the target
  language**.
  - Add them as extra ASS events: a `\p1` rounded-rectangle drawing on layer 1 and the word on layer 2,
    with the same start and end.
  - Measure where the text sits over its whole lifetime, because it may move and flicker. Look at gridded
    frames every 0.2 s, and size each box to cover the full extent plus a margin.
  - End the boxes exactly at the scene cut; find it with frame differences at 30 fps.
  - Check a 0.2 s grid of the render to confirm that nothing peeks out.
  - For whole caption tracks, use `burned_captions.py` instead (see SKILL.md step 2).
- Burned-in captions (video23, white rounded boxes with black text): `burned_captions.py detect` read all
  96 captions with their times, and the script was written and timed from them. A plain white-threshold
  box detector missed every box that touched a bright background (white machines, foam). The black-text
  fallback fixed most of them. One 2 s caption still had to be added with `--manual`. Telea inpainting
  plus a feathered blur leaves a soft smudge that the new captions mostly cover.
- Voice speed differs a lot between voices: "äldre kvinna 60+ - SE" read eleven_v4 paragraph takes at
  ~16.5 characters/s (1795 characters → 108.7 s), against ~18 for the video 2 voice. Measure the first
  takes with align_words.py and trim wording before planning. Trimming 80 characters across two
  paragraphs brought the maximum tempo from ~1.14 to 1.02.

- Video31 (720x900, captions in 44 px boxes at y 0.88): `burned_captions.py detect --box-h 44` read all
  606 captions, and the remove step needed one `--manual` box. Cutting parts of the footage (an exhibition,
  the end card) is easiest on the cleaned video with ffmpeg `select='lt(n,A)+between(n,B,C)',setpts=N/30/TB`.
  Map the original line times to the cut timeline before choosing anchors.
- With a music bed the final mix is never quiet, so render.py now measures speech and pauses on the voice
  track (`--audio`) instead of the mix.
- A short exclamation ("Titta här.") came out ~100 Hz above the "Äldre man 50-60 år - SE" voice's median
  in two takes in a row, with a flat contour. A regenerated take fixed the next sentence but not that
  one. Mention such lines to the user rather than regenerating again and again.
- Video32 (Uproot vs Affresh side-by-side test, 131 s → 120 s):
  - Five short competitor-box clips and the end card were cut.
  - Fifteen label cards replaced the English graphics with Norrtvätt's offer: "REA / UPP TILL 50 % / + FRI
    FRAKT", "20 KR PER TABLETT", "30 DAGARS PENGARNA TILLBAKA", and "PASSAR ALLA TVÄTTMASKINER" over an EWG
    logo the user doesn't have.
  - Fly-in icons need a moving card (`path`), and zoom-in titles a shrinking one (`zoom`).
  - Cards back to back must not fade, or the graphic shows through for a few frames.
  - A card may start before its graphic (e.g. in sync with the spoken words), as long as it covers the
    graphic while it is visible.
  - The detector had taken a white "MONEY BACK" badge for the caption box and missed the real caption
    under it. `burned_captions.py` now finds the usual caption row first and prefers candidates on it.
- Cutting a competitor end card (video23, the last 2.4 s): re-run `plan_timeline.py` with
  `--video-duration` at the cut (find it with ffmpeg `select='gt(scene,0.25)',showinfo`), cut the clean
  video with `-frames:v`, then rebuild the voice, captions and render. Drop or widen the late anchors so
  the lost seconds spread over the last ~25 s (x1.07) instead of squeezing the call to action (x1.13).
- After `split_takes.py` replaces sentence clips, `tighten_pauses.py` would restart from the old copies
  in `sent/raw/`. split_takes.py now deletes those stale copies itself.

## Footage and content
- Look for **other brands in the footage** (packaging, websites, logos) and warn the user. Offer to cover
  those shots with the user's product image if they upload one. On Maskinrent video 2 (other session)
  the user chose to keep the competitor's box shots; on video23 and video31 they asked to cut the
  competitor's end card (and on video31 a trade-show clip).
- When the user sends a re-cut of a video you already did, run `analyze_video.py NEW --reference OLD`.
  Unchanged sections keep their timestamps, so earlier anchors can be reused.
- Rendering 1080×1920 for 110 s takes about 3.5 min on the sandbox. Tell the user it's coming.
- GitHub refuses files over 100 MB. render.py's crf 21 gave 182 MB for the 4:49 1080×1908 video2; re-encode
  the final for GitHub with `-b:v 2450k -maxrate 3600k -bufsize 4900k -c:a copy` (94.9 MB) and send the
  chat preview as usual.

## Other languages (Norwegian video2, Nov 2026)
- Norwegian: `language_code: "no"` for eleven_v4, `align_words.py --lang no` (espeak voice nb) and
  `make_captions.py --lang no` (Norwegian small words). The user's own Norwegian voices are in the
  workspace (e.g. "Norsk äldre man 55-60 år"); when the user asks for "the same gender as the Swedish
  version", pick from those with `creative_list_voices(languages=["no"], gender=...)` and name the choice.
- This voice reads story lines livelier than v3 (sentence medians 111-181 Hz around a 132 Hz voice median).
  A regenerated take of the liveliest paragraph came back with the same pitch curve and the same timbre
  (MFCC distance), so it was the delivery, not a second speaker. Compare timbre as well before regenerating
  everything over the ±15 Hz rule.

## Small burned-in captions and long videos (video40, Nov 2026)
- Measure the caption box height before `burned_captions.py detect`: video40's boxes were 34 px high on
  720×1280, and the default `--box-h 55` found only 2 216 of 11 161 frames (150 captions instead of 479).
  With `--box-h 34` every caption was found. Run detect once more on the clean video: it found three
  leftovers (captions raised inside a graphic and a single-frame caption).
- When the planner leaves a long pause before an anchor (2.3 s before the OXYGEN BLEACH title), look at
  the footage there first. A competitor-brand montage (Affresh, OxiClean) could simply be cut (1.9 s),
  which fixed the pause and removed the other brands in one go.
- For a long story (6 min) the voice was ~4 % longer than the picture in the first two minutes and the
  offer at the end. Slowing those stretches of footage by 7-8 % (repeated frames, not blended ones, which
  ghost on moving shots) and the middle by 3 % kept the voice at x0.95-1.05 with every anchor hit.
