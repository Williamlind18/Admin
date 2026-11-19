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

## The seven Swedish winners (use these for every new market)

When the user wants "the winners" or "all winning ads" in a new market or language, use exactly these seven.
They were checked against the live ads in Ads Manager on 2026-11-19, and the length and content match. Don't search
Ads Manager or GitHub for them again. ("Gör alla annonser på norska" still means the closed Norwegian list
below.) Each source is a finished Swedish delivery: footage, Swedish voice, music
and burned-in captions. Fetch it with `git show <branch>:<path>`. The script and the .srt sit next to the mp4
(`manus_*.txt`, same name `.srt`).

| Meta name | Swedish delivery (path @ branch) | Swedish script | Length, size | Speaker |
|---|---|---|---|---|
| b4 C2 (breakthrough) | `leverans/norrtvatt_video22_sv.mp4` @ `claude/quirky-mayer-tsglxb` | `manus_video22.txt` | 3:48, 1080x1920 | man |
| b1 C3 | `leverans/norrtvatt_maskinrent_video2_sv.mp4` @ `claude/inspiring-feynman-uo7z24` | `manus_norrtvatt_video2.txt` | 4:49, 1080x1908 | man |
| b3.1 C8 | `leverans/norrtvatt_maskinrent7_sv.mp4` @ `claude/zealous-dijkstra-nzvyw0` | `manus_maskinrent7.txt` | 3:42, 1080x1368 | man |
| b3 C3 | `leverans/norrtvatt_video11_sv.mp4` @ `claude/quirky-mayer-tsglxb` | `manus_video11.txt` | 4:23, 1080x1908 | man |
| b5 C2 | `leverans/norrtvatt_vsl_reparator.mp4` @ `claude/video-editing-15noqg` | `manus_vsl_reparator.txt` | 3:30, 720x1280 | man |
| b5.1 C3 | `leverans/norrtvatt_video43_tre_enzymer_sv.mp4` @ `claude/focused-hamilton-930j6d` | `manus_video43_tre_enzymer.txt` | 3:51, 720x1280 | woman 30-40 |
| b5 C5 | `leverans/norrtvatt_maskinrent9_enzymer_sv.mp4` @ `claude/funny-rubin-truuco` | `manus_maskinrent9_enzymer.txt` | 0:53, 720x1280 | woman |

- **Ask the user for the voices.** In Danish, the five men's ads used one man aged 40-50, b5.1 C3 a woman aged
  30-40 and b5 C5 a woman aged 40-50.
- **Translate from the Danish scripts** in `leverans/danmark/manus/`. Each has the Danish line with the Swedish
  line under it, 1:1 with the Swedish .srt sentences. Brand and offer are already swapped there.
- **Music beds** for all seven, cut to start at 0 s of each ad, are in `leverans/underlag/musik_vinnare/`.
  - b3.1 C8 loops every 53.058 s and b5.1 C3 every 136.0 s.
  - b1 C3's file has no music, but the live ad does. `musik_b1-C3.mp3` was extracted from the live ad.
  - Match the Swedish voice/music ratio, then loudness-match the result to the Swedish ad (about −15 LUFS).
- **Text-free footage is ready:** `leverans/underlag/textfri_vinnare/textfri_<ad>.mp4`. These are the seven
  winners with the Swedish captions removed by Vmake. They have no audio and are packed to about 93 MB each. Start
  from these; don't spend Vmake credits again. The notes below say what is still left in them.
- **Text removal:** Vmake `SKM0002` removes the captions.
  - It leaves empty boxes where b5 C2's FÖRE/EFTER labels were (2:41-2:44, boxes at x 177 and 550, y 914 in
    720x1280). Put the new language's labels there.
  - b5 C2 ends on the Swedish Maskinrent product card (3:24.6 to the end). Replace it with the market's product
    image.
  - b5.1 C3 ends on a Swedish closing card (3:47.5 to the end). Replace it with a closing card in the market's
    language.
- **Caption height** (`--y`): b4 C2 0.714, b5 C2 0.652, b5.1 C3 0.645, the rest 0.75.
- **Method:** see "Danish versions" in `.claude/skills/ad-video-localizer/references/lessons.md`. The Danish
  delivery is `leverans/danmark/`.

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
