# Notes for Claude

- The user writes in Swedish, so answer in Swedish.
- For any video work, such as translating an ad video, a new voiceover, synced captions or swapping the
  script to the user's product, use the `ad-video-localizer` skill in `.claude/skills/ad-video-localizer/`
  and follow its SKILL.md step by step.
- Standing preferences for video work:
  - ElevenLabs `eleven_v4` with `language_code: "sv"` (the user confirmed v4 on 2026-11-04). Ask for the
    voice ID in every project.
  - Read the script in a few long takes, one per paragraph of 5-8 sentences (all hooks in the first take),
    and cut them into sentences (`split_takes.py` in the account's ad-video-localizer skill). Never
    generate one clip per sentence: it sounds robotic and like different people.
  - Speed the voice up only with `atempo` (the default in `build_voiceover.py`), never rubberband, which
    sounds robotic. Keep speed-ups at or under about 1.08.
  - Cover burned-in foreign text in the footage with white boxes holding black Swedish text.
  - Short pauses of about 0.2 s. Natural, flowing Swedish.
  - Never remove content the user wants to keep.
  - Captions are 1-3 words in Montserrat ExtraBold.
  - While the voice talks about the offer, show ONE offer image with every offer on it (clean, light, centred:
    the store's own NORRTVÄTT logo, product, black pill, offer, a small trust row), hold it as long as needed, then let the
    original footage continue. Never a quick series of product cards (user, 2026-11-09). Logo file:
    `.claude/skills/norrtvatt-iterations/assets/norrtvatt_logo.png` (from the norrtvatt.se header); never redraw it.
  - End an ad with a closing still in the same style that repeats the offer and norrtvatt.se (rating
    "4,8/5" and "15 000+ nöjda kunder" are confirmed). The voiceover does not need to mention it.
  - Never show images back to back (offer image, the original's own product card, closing still). Keep
    at least ~6 s of real footage between the offer image and the closing still; if there is less, end on the
    footage and skip the still. If the offer image would run into another image, cut it when the script moves
    on from the offer (e.g. at "Bättre pris än så här …") and return to the original clips (user, 2026-11-10).
  - Cut clips on the original's scene cuts: no slivers of another shot at the start or end of a clip.
  - Deliver a preview in chat, full quality on GitHub and an .srt file.
- For ad iterations (new versions, hooks or concepts from an existing ad, ad breakdowns, labeling
  winners, planning the next batch), use the `ad-iterations` skill for any brand. For Norrtvätt /
  Maskinrent / Uproot Clean, also use `norrtvatt-iterations`, which holds the brand facts, the ad
  catalogue and the iteration backlog.
- Authority is a requirement in every ad (Spencer's rule, confirmed by the user on 2026-11-04). Every
  brief names who says it and what proves it. The Uproot grandpa is only an example of authority; don't
  fixate on it.
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
