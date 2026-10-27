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
- This repo is public. Never commit API keys or other secrets.

## Norwegian versions ("gör alla annonser på norska")

When the user writes "gör alla annonser på norska", translate ONLY the four ads below to Norwegian.
This is a closed list, fixed on 2026-10-27. Ads made after that date stay Swedish unless the user names
them. The Norwegian version is the same ad (same footage, content, offer and structure) with only the
language changed. Translate from the Swedish script in `leverans/`, and use the source video in the
GitHub release named after the tag.

| Ad | Source (release tag) | Swedish script | Swedish delivery |
|---|---|---|---|
| Maskinrent 3, UV test | `video8` | `leverans/manus_maskinrent3_uvtest.txt` | `leverans/norrtvatt_maskinrent3_uvtest_sv.mp4` |
| Maskinrent 4, biofilm | `video9` | `leverans/manus_maskinrent4_biofilm.txt` | `leverans/norrtvatt_maskinrent4_biofilm_sv.mp4` |
| Maskinrent 5, three mistakes | `video17` | `leverans/manus_maskinrent5_tremisstag.txt` | `leverans/norrtvatt_maskinrent5_tremisstag_sv.mp4` |
| Maskinrent 6, mold | `video19` | `leverans/manus_maskinrent6_mogel.txt` | `leverans/norrtvatt_maskinrent6_mogel_sv.mp4` |
