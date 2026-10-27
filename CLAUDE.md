# Notes for Claude

- The user writes in Swedish, so answer in Swedish.
- For any video work, such as translating an ad video, a new voiceover, synced captions or swapping the
  script to the user's product, use the `ad-video-localizer` skill in `.claude/skills/ad-video-localizer/`
  and follow its SKILL.md step by step.
- Standing preferences for video work:
  - ElevenLabs `eleven_v3`. Ask for the voice ID in every project.
  - Read the whole script in ONE take and cut it into sentences with `split_take.py`. Never generate one
    clip per sentence: it sounds robotic and like different people.
  - Speed the voice up only with `atempo` (the default in `build_voiceover.py`), never rubberband, which
    sounds robotic. Keep speed-ups at or under about 1.08.
  - Never slow the voice down. A 5 % slow-down (video 15) made eleven_v3's lengthened word endings sound
    drawn out ("tvätte---n", "slu---t"). Spread spare time over the pauses instead (`--max-gap 0.6`).
  - Cover burned-in foreign text in the footage with white boxes holding black Swedish text.
  - Short pauses of about 0.2 s. Natural, flowing Swedish.
  - Never remove content the user wants to keep.
  - Captions are 1-3 words in Montserrat ExtraBold.
  - Deliver a preview in chat, full quality on GitHub and an .srt file.
- Norwegian versions: when the user writes "gör alla annonser på norska", make Norwegian versions of
  ONLY the four ads listed in `leverans/norska/README.md` (videos 5, 11, 14 and 15, made 2026-09-29 to
  2026-10-14), and follow that README. Swedish ads made later, and the older Maskinrent videos, are not
  included unless the user names them.
- This repo is public. Never commit API keys or other secrets.
