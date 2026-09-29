---
name: ad-video-localizer
description: "Localize or re-voice short-form ad videos (TikTok, Reels, Shorts, UGC ads): translate or rewrite the voiceover script for a new language, brand, product and offer, generate the new voiceover with the user's ElevenLabs voice (eleven_v3, the whole script in one continuous take that is then split into sentences), fit it to the video's length and key visuals with short natural pauses, and burn in word-synced captions plus an .srt file. Use this skill whenever the user wants to translate or dub a video, replace a voiceover, adapt a competitor's or supplier's ad to their own product or website, add synced captions or subtitles to a voiceover, or mentions ElevenLabs together with a video - also when they write in Swedish, e.g. 'översätt videon till svenska', 'lägg in synkade captions', 'ny voiceover med min röst', 'byt manuset till min produkt', 'redigera reklamvideon', even if they never say localize."
compatibility: "Needs Bash + Python 3 with pip and internet for setup (ffmpeg via imageio-ffmpeg, librosa, espeak-ng, Google Fonts) and the ElevenLabs connector (or an ELEVENLABS_API_KEY environment secret). Built and tested in the Claude Code cloud sandbox."
---

# Ad video localizer

This skill turns an existing short-form ad into a new version:

1. A new script, translated or adapted to the user's brand.
2. The user's ElevenLabs voice speaking it.
3. The voice timed to the footage.
4. Word-synced captions burned into the picture.

It was built from real projects the user was very happy with. The scripts in `scripts/` encode what
worked, so run them instead of improvising new tooling. Talk to the user in their language (Swedish
for the original user), and keep them posted during slow steps (a whole-script voice take ~2-3 min,
render ~3-4 min).

## The user's standing preferences
- **Voice:** ElevenLabs **eleven_v3** with the voice ID they give for *this* project. Ask every time;
  the ID changes and none is stored.
- **One take, one speaker.** Generate the **whole script in one continuous take** and split it into
  sentences with `split_take.py`. Never generate one clip per sentence: every eleven_v3 call varies
  timbre, stress and pronunciation, and the user heard it as "robotic and like two different people".
- **Natural speed-ups only.** Stretch with **atempo** (the default in `build_voiceover.py`). The
  rubberband filter made the voice sound metallic/robotic from the first sped-up sentence on; the
  unstretched opening sounded "perfect". Keep speed-ups small (aim ≤ 1.08).
- **Pauses:** short and even, about 0.2 s between sentences. Long gaps were the main complaint.
- **Script:** natural, flowing target language. You may rephrase for flow and fit, and should adapt it to
  their product, prices and offers.
- **Never remove content the user wants kept.** Flag risky claims once and let them decide.
- **Captions:** 1-3 words at a time, bold white Montserrat ExtraBold with a black outline, placed over
  the old captions (about 75 % down the frame).
- **Delivery:** a preview in chat, full quality on GitHub, and an .srt file.

## Workspace
Use a folder in the scratchpad, e.g. `WORK=<scratchpad>/<project>`, and `SK=<this skill>/scripts`.

```
WORK/src.mp4            source video
WORK/script.txt         approved script, one sentence per line
WORK/take.mp3           the whole script read in one eleven_v3 take
WORK/sent/NN.txt|mp3    per-sentence text + clip cut from take.mp3; iso.mp3 = word reference
WORK/sent/fused.json    word timings        WORK/sent/plan.json   timeline
WORK/vo.wav, words_global.json, captions.ass, subtitles.srt, final.mp4, preview.mp4
```

## Steps

### 0. Setup (once per session)
`bash $SK/setup.sh $WORK` installs ffmpeg, librosa, espeak-ng and the caption font, then prints
which filters are available.

### 1. Intake
Ask in **one** message for whatever is missing:
- **The video.** See `references/delivery.md`. Files over 25 MB go through a GitHub release.
- **The original voiceover text.** You cannot transcribe audio here.
- **Target language**, and whether to translate directly or adapt.
- **The ElevenLabs voice ID.** Check that the ElevenLabs connector tools are available; see
  `references/elevenlabs.md`.
- **Product facts.** Try WebFetch on their page first; it is often blocked, so ask for screenshots.
- **Lines or claims that must stay**, and whether they have music to put under the voice.

### 2. Look at the video
`python3 $SK/analyze_video.py WORK/src.mp4 --out WORK/analysis` (add `--reference OLD.mp4` for a
re-cut of a video you have done before). Open the `sheet_NN.png` contact sheets with the Read tool.
Note down:
- **Key visual moments** a line must hit, e.g. "this", a close-up, before/after shots, the product
  appearing. Use the scene-cut times to get exact seconds.
- **Where old captions sit**, often as blurred bars. The default y = 0.75 usually covers them.
- **Background music** (the audio report says so). It cannot be separated, so warn the user now.
- **Other brands visible in the footage**, and any burned-in text that will remain.

### 3. Write the script
Follow `references/script-writing.md`. Save the result as `WORK/script.txt`, one sentence per line, in
spoken order. Then check the length:
`python3 $SK/split_script.py WORK/script.txt WORK/sent --video-duration D [--rate R]`.
The speaking rate depends on the voice. For a voice you have not measured, check its rate first (see
`references/elevenlabs.md`).
Show the user the complete numbered script and get approval before spending credits. Mention any
compliance flags once in that same message.

### 4. Generate the voice
Follow `references/elevenlabs.md`. You need:
- **one** `eleven_v3` take of the **whole script** (the lines of `script.txt` joined with spaces,
  `generations_count: 1`), saved as `WORK/take.mp3`,
- one cheap `eleven_flash_v2_5` word-by-word reference made from `sent/iso.txt`, saved as `sent/iso.mp3`.

Download with `bash $SK/download_clips.sh urls.txt WORK` (names `take` and `iso`, then move
`iso.mp3` into `sent/`). Then cut the take into sentences:
`python3 $SK/split_take.py WORK/take.mp3 WORK/sent`. Check its table: every `pause_after` should be a
real sentence pause (≥ ~0.35 s; v3 takes usually have 0.4-0.8 s) and no row should be marked
`<-- check`. Keep a running total of credits for the report.

### 5. Find the word timings
`python3 $SK/align_words.py WORK/sent --lang sv`. For each boundary it takes the median of three
estimates (syllables, espeak DTW, same-voice reference DTW). This was checked against the original
project and reproduced its timings exactly. Note sentences whose "spread" is 0.6 s or more; those are
the least certain.

### 6. Plan the timeline
```
python3 $SK/plan_timeline.py WORK/sent --video-duration D \
    [--order 1,2,...] --anchor 9:end=44.3-46.6 --anchor 19:start=87.4-89.6
```
- **Anchors.** Only add anchors for the key moments from step 2, with a window of about ±1 s around
  each. `end` anchors suit lines whose pointing word comes last. `start` anchors suit lines that open
  on the visual.
- **Max tempo.** The planner lays sentences out with 0.18 s gaps and picks one tempo per block between
  anchors, keeping the highest as low as possible. Aim for **≤ 1.08**, and **≤ 1.10** only for the final
  offer/CTA section (a one-take voice usually lands at 1.00-1.09). Anchor windows can be narrow
  (±0.3 s) when the tempos have room. If the tempo is higher, fix the script, not the speed:
  - move generic lines in front of an anchor with `--order` (the order file can differ from the
    numbering),
  - tighten wording,
  - drop "if it fits" extras.
  Ask the user before cutting anything they asked for.
- **Gaps before an anchor.** If the voice runs ahead of the footage and leaves a long gap before an
  anchor, it is usually because a condensed passage lost detail. Restore some of it.
- **Changed sentences.** Settle the script *before* the take. A sentence generated on its own later
  sounds like a different speaker, and a re-take is not guaranteed to be shorter (a trimmed line once
  came back 0.3 s longer). For a changed line, generate a new whole take (≈1 credit per character)
  and rerun split_take + steps 5-6. Also add an `isoNN.mp3` word reference for the changed sentence,
  or regenerate `iso.mp3` if many lines changed. Patch in a single sentence only when the user accepts
  the risk that it sounds different.

### 7. Build the voice track and captions
```
python3 $SK/build_voiceover.py WORK/sent --out WORK/vo.wav
python3 $SK/make_captions.py WORK/words_global.json --video WORK/src.mp4 --out-dir WORK --lang sv
```
`build_voiceover.py` speeds up with atempo by default. Do not switch to `--stretch rubberband`: it
sounded robotic to the user. Captions can be tuned with `--y` (vertical position), `--font`,
`--size`, `--max-words`, `--max-chars` and `--upper`. Read the printed chunk list and fix any clumsy
splits, e.g. "tre lager: filmen" should become "tre lager | filmen". See `references/lessons.md`
for hand-picked chunks and for covering burned-in foreign text with label boxes.

### 8. Render and check
```
python3 $SK/render.py --video WORK/src.mp4 --audio WORK/vo.wav --ass WORK/captions.ass \
    --fonts WORK/fonts --out WORK/final.mp4 --preview WORK/preview.mp4 --check-frames 44.2,90.0 \
    [--bed music.mp3 --bed-db -16]
```
The QA line must show 0.00 s of speech without a caption and no unintended pauses over 0.5 s. Open
the check frames at the anchor times with Read, and confirm that the caption shown matches the visual
(e.g. "det här" on the close-up).

### 9. Deliver
Follow `references/delivery.md`:
- Send the preview, the .srt and the script via the chat file tool (30 MB limit).
- Commit and push the full-quality mp4 to the working branch and link it.
- Report what changed, any timing trade-offs, warnings, and the credits used.

## When things go wrong
See `references/lessons.md`. It covers:
- the blocked hosts,
- why the voice must be one take that is split, not one clip per sentence, and why atempo beats rubberband,
- why Scribe transcripts don't help,
- what to do when music, competitor branding or old burned-in text is in the footage.

## Security
Never store API keys, tokens or passwords in this skill, the repo, commit messages or chat. Use the
ElevenLabs connector, or an environment secret named `ELEVENLABS_API_KEY`. If the user pastes a key,
advise them to rotate it.
