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
