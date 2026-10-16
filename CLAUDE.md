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
- For any product page copy, use the user's five-section template as a guiding thread (it converts well for
  them), not a rigid rule. Below the buy box:
  1. Image + text that stirs emotion and recognition in the avatar and names the problems in their everyday life.
  2. Image + text that introduces the product, its USPs, how it works and how it solves the problems from section 1.
  3. Image + text with bullet points, each with an explanatory subheading.
  4. Guarantee (the user's default is 30 days; use the product's real terms, e.g. 60 days for the PDRN stick).
  5. Reviews (only genuine reviews; never invent reviews, ratings or customer counts).
  Base the copy on the avatar: the better the avatar is known, the better the conversion. Feel free to add
  sections, reorder or take other angles whenever that suits the avatar better.
- This repo is public. Never commit API keys or other secrets.
