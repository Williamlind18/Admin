# Notes for Claude

- The user writes in Swedish, so answer in Swedish.
- For any video work, such as translating an ad video, a new voiceover, synced captions or swapping the
  script to the user's product, use the `ad-video-localizer` skill in `.claude/skills/ad-video-localizer/`
  and follow its SKILL.md step by step.
- Standing preferences for video work:
  - ElevenLabs `eleven_v4` with `language_code: "sv"`. Ask for the voice ID in every project.
  - Read the script in paragraph takes of 6-9 sentences, never one sentence per generation.
    Per-sentence takes made the voice sound like different people, and once like a woman.
    Split each take into sentence clips with `split_takes.py`, then run `tighten_pauses.py`.
  - The voice must be one consistent speaker. Check pitch per sentence and regenerate the whole
    paragraph take if a sentence deviates.
  - Natural speed: never speed the voice up past about x1.08, because it sounds robotic. A slow-down
    of up to 5 % (`plan_timeline.py --min-tempo 0.95`) is fine.
  - Stretch with atempo (the `build_voiceover.py` default), never rubberband: it sounded metallic/robotic.
  - v4 has a slight echo. Offer the ElevenLabs Voice Isolator (about 1 000 credits per minute) rather
    than running it unasked.
  - Pauses of about 0.2-0.3 s, never over about 0.5 s. Natural, flowing Swedish.
  - Write every voice script for the ear (any person or tone), as in
    `.claude/skills/ad-video-localizer/references/script-writing.md` "Writing for a lively, human voice":
    - short, varied sentences with a short punch after a long one, and a colon before a reveal;
    - the key word last, lists of three or contrasts, and concrete names, numbers and objects;
    - spoken Swedish ("sen", active verbs) and "du" to the listener;
    - no exclamation marks, caps or symbols, and no lone one- or two-word lines.
  - Never remove content the user wants to keep.
  - Captions are 1-3 words in Montserrat ExtraBold.
  - Deliver a preview in chat, full quality on GitHub and an .srt file.
- This repo is public. Never commit API keys or other secrets.

## Norwegian versions ("gör alla annonser på norska") in this session
In this session (branch `claude/inspiring-feynman-uo7z24`, session 01YTjhMMtce8VYyMS9aqb9JF) that command
means ONLY the ad listed in `leverans/norska_underlag/inspiring-feynman.md`: the Maskinrent "repairman,
19 years, biofilm" ad, `leverans/norrtvatt_maskinrent_video2_sv.mp4`. This is a closed list, fixed on
2026-10-27. Swedish ads made later in this session are NOT included unless the user names them, and
neither are older ads from other sessions. The file also says how to make the Norwegian version.
