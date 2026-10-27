# Notes for Claude

- The user writes in Swedish, so answer in Swedish.
- For any video work, such as translating an ad video, a new voiceover, synced captions or swapping the
  script to the user's product, use the `ad-video-localizer` skill in `.claude/skills/ad-video-localizer/`
  and follow its SKILL.md step by step.
- Standing preferences for video work:
  - ElevenLabs `eleven_v3`, one clip per sentence. Ask for the voice ID in every project.
  - Short pauses of about 0.2 s. Natural, flowing Swedish.
  - Never remove content the user wants to keep.
  - Captions are 1-3 words in Montserrat ExtraBold.
  - Deliver a preview in chat, full quality on GitHub and an .srt file.
- Norwegian versions: when the user writes "gör alla annonser på norska", translate only the ads listed
  in `leverans/norska_annonser.md` (list locked 2026-10-27). Ads made after that date are not included
  unless the user asks for them by name or asks to add them to the list.
- This repo is public. Never commit API keys or other secrets.
