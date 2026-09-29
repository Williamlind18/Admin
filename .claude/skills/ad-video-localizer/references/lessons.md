# Lessons learned and troubleshooting

## Environment (Claude Code cloud sandbox)
- **ffmpeg:** comes from the `imageio-ffmpeg` wheel (PyPI works). It has **no `drawtext` filter**, so
  all on-screen text goes through ASS subtitles (the `ass` filter, libass) with `fontsdir`.
  `rubberband` is available for pitch-preserving tempo changes.
- **Reachable:** PyPI, Ubuntu apt (archive.ubuntu.com), Google Fonts, the session's GitHub repo and its
  releases, storage.googleapis.com (ElevenLabs downloads).
- **Blocked:** Hugging Face, OpenAI model CDN, download.pytorch.org, Dropbox, Google Drive,
  WeTransfer, most shop domains, and api.elevenlabs.io unless the user allows it.
- There is no speech recognition, and you cannot listen to audio. Everything about timing comes from
  signal analysis plus the known text. Say so honestly and ask the user to check the result.

## Audio
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
- Keep captions to 1-3 words, with no dangling "det / och / ditt" at the end of a chunk. That is already
  handled by make_captions.py.

## Footage and content
- Look for **other brands in the footage** (packaging, websites, logos) and warn the user. Offer to cover
  those shots with the user's product image if they upload one.
- When the user sends a re-cut of a video you already did, run `analyze_video.py NEW --reference OLD`.
  Unchanged sections keep their timestamps, so earlier anchors can be reused.
- Rendering 1080×1920 for 110 s takes about 3.5 min on the sandbox. Tell the user it's coming.
