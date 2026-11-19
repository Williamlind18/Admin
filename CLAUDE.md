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
- To remove watermarks, logos or burned-in text, or to restore or upscale images and video with Vmake, use the
  `vmake-skill` skill in `.claude/skills/vmake-skill/`. It is a paid API, so ask before uploading. Its keys are
  `MT_AK`/`MT_SK`, in environment variables or the gitignored `scripts/.env`.
- This repo is public. Never commit API keys or other secrets.

## The launch set: the 26 videos every new market gets

These are the Norwegian ads in Ads Manager: "Ad account 3", campaign "CBO - Norrtvätt NO", ad sets A1 - Hero and
A2-A5 with ads C1-C5. That is 25 ads and 26 videos, because A2 C5 runs one ad in two formats. They were matched to
their files by length on 2026-11-19. Don't search Ads Manager or GitHub for them again.

- **Before every launch in a new market or language, make exactly these 26 first, and nothing else,** unless the
  user names more. "Gör alla annonser på <språk>" and "gör lanseringsannonserna för <land>" mean these 26.
- **Same ad, new language.** Keep the footage, content, offer and structure. Change only the language, brand
  name, currency and domain. Translate from the Swedish script, and use the Norwegian one as support. Scripts and
  .srt files sit next to the videos (`manus_*.txt`, same name `.srt`).
- **Ask the user first,** before anything costs credits: the voices (gender and age per ad), the brand and
  product names, the price in local currency and the domain.
- **Already in Danish:** A1 C1, A1 C2 and A1 C3 are among the seven winners below (b1 C3, b3 C3 and b3.1 C8).

| Meta | Ad | Norwegian delivery (`leverans/`) @ branch | Swedish source (`leverans/`) @ branch | Length |
|---|---|---|---|---|
| A1 C1 | Maskinrent video 2 (= b1 C3) | `norrtvatt_maskinrent_video2_no.mp4` @ `claude/inspiring-feynman-uo7z24` | `norrtvatt_maskinrent_video2_sv.mp4` @ same | 4:49 |
| A1 C2 | video11 (= b3 C3) | `norrtvatt_video11_no.mp4` @ `claude/quirky-mayer-tsglxb` | `norrtvatt_video11_sv.mp4` @ same | 4:23 |
| A1 C3 | Maskinrent 7 (= b3.1 C8) | `nordvask_maskinren7_no.mp4` @ `claude/zealous-dijkstra-nzvyw0` | `norrtvatt_maskinrent7_sv.mp4` @ same | 3:42 |
| A1 C4 | Maskinrent 4, biofilm | `nordvask_maskinren4_biofilm_no.mp4` @ `main` | `norrtvatt_maskinrent4_biofilm_sv.mp4` @ `main` | 5:13 |
| A1 C5 | video32 | `norrtvatt_maskinrent_video32_no.mp4` @ `claude/inspiring-feynman-uo7z24` | `norrtvatt_maskinrent_video32_sv.mp4` @ same | 2:00 |
| A2 C1 | Three mistakes | `nordvask_tre_feil_no.mp4` @ `claude/ecstatic-thompson-it7k4c` | `norrtvatt_tre_misstag_sv.mp4` @ same | 2:20 |
| A2 C2 | Maskinrent 2 | `nordvask_maskinren2_no.mp4` @ `claude/ecstatic-thompson-it7k4c` | `norrtvatt_maskinrent2_sv.mp4` @ same | 2:15 |
| A2 C3 | Maskinrent 1 | `nordvask_maskinren_no.mp4` @ `claude/ecstatic-thompson-it7k4c` | `norrtvatt_maskinrent_sv.mp4` @ same | 1:50 |
| A2 C4 | Maskinrent 3, 30 s version | `nordvask_maskinren3_no.mp4` @ `claude/focused-hamilton-930j6d` | `norrtvatt_maskinrent3_sv.mp4` @ same | 0:30 |
| A2 C5 | video25, sale ends (4:5 and 9:16) | `nordvask_video25_salget_slutter_no.mp4` (4:5) @ `claude/focused-hamilton-930j6d`; the 9:16 version is only in Meta | `norrtvatt_video25_rean_slutar_idag_sv.mp4` @ same | 0:20 |
| A3 C1 | video5 | `norrtvatt_video5_no.mp4` @ `claude/quirky-mayer-tsglxb` | `norrtvatt_video5_sv.mp4` @ same | 4:05 |
| A3 C2 | Maskinrent 4 | `nordvask_maskinren4_no.mp4` @ `claude/zealous-dijkstra-nzvyw0` | `norrtvatt_maskinrent4_sv.mp4` @ same | 4:09 |
| A3 C3 | Maskinrent 3, 4-minute version | `nordvask_maskinren3_no.mp4` @ `claude/zealous-dijkstra-nzvyw0` | `norrtvatt_maskinrent3_sv.mp4` @ same | 4:00 |
| A3 C4 | video15 | `norrtvatt_video15_no.mp4` @ `claude/quirky-mayer-tsglxb` | `norrtvatt_video15_sv.mp4` @ same | 2:00 |
| A3 C5 | video14 | `norrtvatt_video14_no.mp4` @ `claude/quirky-mayer-tsglxb` | `norrtvatt_video14_sv.mp4` @ same | 1:25 |
| A4 C1 | Maskinrent 6 | `nordvask_maskinren6_no.mp4` @ `claude/zealous-dijkstra-nzvyw0` | `norrtvatt_maskinrent6_sv.mp4` @ same | 0:59 |
| A4 C2 | Maskinrent 5 | `nordvask_maskinren5_no.mp4` @ `claude/zealous-dijkstra-nzvyw0` | `norrtvatt_maskinrent5_sv.mp4` @ same | 0:56 |
| A4 C3 | Maskinrent 3, UV test | `nordvask_maskinren3_uvtest_no.mp4` @ `main` | `norrtvatt_maskinrent3_uvtest_sv.mp4` @ `main` | 1:42 |
| A4 C4 | Maskinrent 8 | `nordvask_maskinren8_no.mp4` @ `claude/zealous-dijkstra-nzvyw0` | `norrtvatt_maskinrent8_sv.mp4` @ same | 1:02 |
| A4 C5 | Maskinrent 5, three mistakes | `nordvask_maskinren5_trefeil_no.mp4` @ `main` | `norrtvatt_maskinrent5_tremisstag_sv.mp4` @ `main` | 2:16 |
| A5 C1 | video31 | `norrtvatt_maskinrent_video31_no.mp4` @ `claude/inspiring-feynman-uo7z24` | `norrtvatt_maskinrent_video31_sv.mp4` @ same | 4:29 |
| A5 C2 | video23 | `norrtvatt_maskinrent_video23_no.mp4` @ `claude/inspiring-feynman-uo7z24` | `norrtvatt_maskinrent_video23_sv.mp4` @ same | 1:46 |
| A5 C3 | Maskinrent 6, mold | `nordvask_maskinren6_mugg_no.mp4` @ `main` | `norrtvatt_maskinrent6_mogel_sv.mp4` @ `main` | 1:40 |
| A5 C4 | video30, NASA enzymes | `nordvask_video30_nasa_enzymer_no.mp4` @ `claude/focused-hamilton-930j6d` | `norrtvatt_video30_nasa_enzymer_sv.mp4` @ same | 4:08 |
| A5 C5 | video33, service technician | `nordvask_video33_servicetekniker_no.mp4` @ `claude/focused-hamilton-930j6d` | `norrtvatt_video33_servicetekniker_sv.mp4` @ same | 6:39 |

`nordvask_maskinren3_no.mp4` and `norrtvatt_maskinrent3_sv.mp4` exist in two different ads under the same name.
Take the 30 s one from `claude/focused-hamilton-930j6d` (A2 C4) and the 4-minute one from
`claude/zealous-dijkstra-nzvyw0` (A3 C3).

## The seven Swedish winners

When the user asks for "the winners" or "all winning ads", use exactly these seven. For a launch in a new market,
use the launch set above. Three of the seven are in it, and the notes below apply when they are made. The seven
were checked against the live ads in Ads Manager on 2026-11-19, and the length and content match. Don't search
Ads Manager or GitHub for them again. Each source is a finished Swedish delivery: footage, Swedish voice, music
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

## Norwegian versions

All 26 ads in the launch set exist in Norwegian; their files are in the launch-set table. The old closed list of
four (2026-10-27) is part of the set. The original competitor footage for those four is in the GitHub releases
`video8` (Maskinrent 3, UV test), `video9` (4, biofilm), `video17` (5, three mistakes) and `video19` (6, mold).
