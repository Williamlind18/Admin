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
  - Cover burned-in foreign text in the footage with white boxes holding black Swedish text.
  - Short pauses of about 0.2 s. Natural, flowing Swedish.
  - Never remove content the user wants to keep.
  - Captions are 1-3 words in Montserrat ExtraBold.
  - Deliver a preview in chat, full quality on GitHub and an .srt file.
- To remove watermarks, logos or burned-in text, or to restore or upscale images and video with Vmake, use the
  `vmake-skill` skill in `.claude/skills/vmake-skill/`. It is a paid API, so ask before uploading. Its keys are
  `MT_AK`/`MT_SK`, in environment variables or the gitignored `scripts/.env`.
- "Gör alla annonser på norska" means ONLY the ads listed in `annonser/lista1_2026-10-27/README.md`
  (21 image ads, 1 video, 1 copy text, locked 2026-10-27). Ads made after that date are never included, even
  if they are Swedish and made in the same session. Keep each ad the same; only the language changes.
- This repo is public. Never commit API keys or other secrets.
