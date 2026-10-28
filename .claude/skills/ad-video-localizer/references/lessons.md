# Lessons learned and troubleshooting

## Environment (Claude Code cloud sandbox)
- **ffmpeg:** comes from the `imageio-ffmpeg` wheel (PyPI works). It has **no `drawtext` filter**, so
  all on-screen text goes through ASS subtitles (the `ass` filter, libass) with `fontsdir`.
  Tempo changes use `atempo`. `rubberband` is also installed, but don't use it for voice (see Voice).
- **Reachable:** PyPI, Ubuntu apt (archive.ubuntu.com), Google Fonts, the session's GitHub repo and its
  releases, storage.googleapis.com (ElevenLabs downloads).
- **Blocked:** Hugging Face, OpenAI model CDN, download.pytorch.org, Dropbox, Google Drive,
  WeTransfer, most shop domains, and api.elevenlabs.io unless the user allows it.
- There is no speech recognition, and you cannot listen to audio. Everything about timing comes from
  signal analysis plus the known text. Say so honestly and ask the user to check the result.

## Voice (learned on Maskinrent video 2)
- **One clip per sentence sounds like different people.** eleven_v3 varies timbre, stress and
  pronunciation between calls, and the user heard the joined clips as robotic and uneven. Generate the
  **whole script in one take** and cut it with `split_take.py` instead.
- **rubberband sounds robotic; atempo does not.** In a render the opening 9 s were unstretched
  (tempo 1.00) and the rest sped up 5-8.5 % with rubberband. The user said: "perfect for 9 seconds,
  then it went back to the robotic sound". The same take sped up with `atempo` sounded "so much
  better". `build_voiceover.py` now uses atempo by default.
- A continuous take reads ~4 % faster than per-sentence clips and has clean 0.4-0.8 s sentence pauses,
  so the planner usually needs only 1.00-1.09.
- A re-generated sentence is not guaranteed to be shorter, even with fewer words: a trimmed line came
  back 0.3 s longer. Settle the wording before the take.
- The user's subscription allows 5 concurrent ElevenLabs requests; more fail with "Too many
  concurrent requests" and must be started again.

## Audio
- If the original ad has music under the voice, it cannot be separated here (source-separation models
  are blocked). The output is voice-only unless the user supplies the music file. Mix it with
  `render.py --bed music.mp3 --bed-db -16`.
- The loudness target -14 LUFS (`loudnorm`) suits TikTok, Reels and Shorts.
- eleven_v3 speaks about 13 % slower than multilingual_v2, so budget for it.
- With atempo, up to about 1.08× tempo is inaudible. Keep the offer/CTA section at or under about 1.10×.
  Above that, fix the script instead.

## Timing and captions
- The user dislikes long pauses. Use 0.18 s between sentences and cap pauses at 0.45 s. Anchored
  sentences get 0.3 s around them.
- Syncing the ~3 key visual moments matters more than following the original timing everywhere. Anchor
  only those.
- `align_words.py` "spread" column: this is how far the three methods disagree (median, seconds).
  Values ≤ 0.3 s are normal. For sentences with ≥ 0.6 s, look at the chunk timings more carefully in
  the check frames, and mention them to the user as places to double-check.
- Place captions where the old captions were (often blurred bars around 75 % of the height, visible on
  the contact sheets), so the new text covers them. Burned-in original text elsewhere cannot be removed.
  Say so.
- Keep captions to 1-3 words, with no dangling "det / och / ditt" at the end of a chunk. That is already
  handled by make_captions.py. Still read the chunk list: it splits blindly at colons and lists
  ("tre lager: filmen" → "lager filmen"). When several are clumsy, write the chunks by hand, one line
  per sentence with chunks separated by `|`, and build the Dialogue lines from `words_global.json`
  with the same style and timing rule as make_captions.py (Maskinrent video 2 did this).
- **Burned-in foreign text** in the footage (e.g. English labels "FILM / PROTEIN / GREASE" on a close-up):
  the user wanted it covered by **white rounded boxes with black Montserrat ExtraBold text in the
  target language**. Add them as extra ASS events: a `\p1` rounded-rectangle drawing on layer 1 and the
  word on layer 2, with the same start/end. Measure where the text sits over its whole lifetime (it
  may move and flicker). Look at gridded frames every 0.2 s, and size each box to cover the full
  extent plus a margin. End the boxes exactly at the scene cut; find it with frame differences at
  30 fps. Then check a 0.2 s grid of the render to confirm that nothing peeks out.

## Footage and content
- Look for **other brands in the footage** (packaging, websites, logos) and warn the user. Offer to cover
  those shots with the user's product image if they upload one. On Maskinrent video 2 the user chose
  to keep the competitor's box shots.
- When the user sends a re-cut of a video you already did, run `analyze_video.py NEW --reference OLD`.
  Unchanged sections keep their timestamps, so earlier anchors can be reused.
- Rendering 1080×1920 for 110 s takes about 3.5 min on the sandbox. Tell the user it's coming.

## Short ads and end cards (learned on Maskinrent video 3, 30 s)
- **Voices differ in speed.** The voice "30 år kvinna" spoke about 15.3 characters per second, not the
  16.3 that `split_script.py` assumes. The first take (487 characters, estimated ×1.07) needed ×1.14.
  Trimming 36 characters of wording without losing content ("tvättmaskinen" → "maskinen", dropping
  "fortfarande", "De har NASA-klassade enzymer som …" → "NASA-klassade enzymer …") and a new take
  gave ×1.00-1.06. With a voice you haven't measured yet, aim for an estimate of ≤ ×1.00 before the take.
- In a short ad the original's timestamps were almost the same as the scene cuts, and the unanchored
  plan already landed within ~0.3 s of every key visual. One anchor (the NASA line on the microscope/
  astronaut shot) was enough. More anchors pushed single blocks up to ×1.16.
- The original had no price. The user wanted the offer anyway, and a 30 s voice has no room for it, so it
  went on an **end card** instead (`make_endcard.py` + `render.py --overlay`): the product photo, and
  under it a white box saying "HÖSTREA / Upp till 50 % rabatt", from the CTA to the end.
- **Product photo:** the store domain was blocked, and the connected Shopify connector belonged to a
  different store (Hjärtelag SE, not Norrtvätt). Cropping the product photo from the user's screenshot
  (about 520 px, scaled up to about 560 px) looked sharp enough.
- On this video the user said the competitor's box may stay visible, the same as on video 2.

## Removing the original text with Vmake (learned on video25, 20 s)
- The user wanted all burned-in text removed and replaced by their own. Vmake "Smart - Video Smart
  Removal" (SKM0003) removed a large static headline ("UPROOT CLEAN / BUY 2 GET 2 FREE / LAST CHANCE /
  ONLY $9.99/PACK", about the top 40 % of the frame) from a 20 s 720×900 video in about 30 s. One paid run.
- The video came back at 23.93 fps instead of 23.98, 0.1 s shorter, with its own audio (which isn't
  used). Use the cleaned file as the video source and its duration for planning.
- Where the removed text lay over packaging text, that text is smeared. A new headline in the same
  place (`make_text_overlay.py`) hides most of it. Swedish equivalents with the user's real offer:
  "NORRTVÄTT / 2-PACK −40 % / SISTA CHANSEN / ENDAST 25 KR/TABLETT".
- The script for a 20 s ad came out at 15.4 s of speech with "kvinna energisk - SE", so the voice ends
  about 2.7 s before the video. Pauses are capped at 0.45 s. The alternative is a spoken CTA line, which
  needs a new whole take.
- A release that is only a draft can't be fetched from github.com/…/releases/download (404) or with the
  built-in `gh api` (it refuses the redirect). `curl -L -H "Accept: application/octet-stream"
  https://api.github.com/repos/OWNER/REPO/releases/assets/ASSET_ID` works. Find ASSET_ID with
  `gh api repos/OWNER/REPO/releases`, which also lists drafts.
- Check that the uploaded video matches the script before paying for anything. Video24 was a 3:43 ad
  that had nothing to do with the 20 s transcript. The right file was video25.

## A 4-minute ad with everything replaced (learned on video30)
- **No script from the user.** Scribe transcribed the original with word times (1,136 words, 243 s).
  The Swedish script had to be condensed to about 60 % (3,941 characters) to fit, while every story
  step was kept. One eleven_v3 take of all 3,941 characters worked; check it first with `estimate_only`.
- **The voice "Äldre man 50-60 år - SE" pauses only 0.12-0.33 s between sentences.** `split_take.py`
  marked almost every row `<-- check`, but the ratios were 0.7-1.26 and the alignment spreads were
  mostly ≤ 0.3 s, so the cuts were right. Check the ratios and spreads before regenerating anything.
- **Anchors.** Fifteen anchors pushed blocks to ×1.15-1.17. Seven anchors with ±2 s windows gave at
  most ×1.06. Adding anchors can raise the tempo of *earlier* blocks. Labels that appear a couple of
  seconds before the voice names them (the enzyme names) are fine.
- **What Vmake (SKM0003) left behind on a long video:**
  - It removed the plain captions and most of the flat labels.
  - It did not remove glowing or stylised price text ("GET 2 FREE", "$9.99 per box"), badges (one
    was removed but left a gray smear, the other stayed), or labels printed on 3D objects ("Alpha
    Amylase", "Protease", "Lipase").
  - It damaged an icon in an animated graphic.
  - It turned 6.6 s of black frames at the end into noise. Trim the end or cover it with an end card.
  - Always scan the cleaned video at 1 fps before building overlays.
- **Fixes that worked:**
  - White boxes with black text over the leftover text, timed to the exact shot cuts (found with frame
    differences).
  - Swedish badges with claims from the user's page ("AVKALKAR", "PASSAR ALLA TVÄTTMASKINER") in place
    of claims we don't make (EWG, septic safe).
  - Redrawn check marks.
  - For the animated "PET HAIR = PROTEIN / SEBUM = FAT" graphic, the original footage was spliced back
    in for those 1.7 s. Only the words that differ in Swedish were covered, with paper-texture patches
    copied from the same frame: DJURHÅR and FETT.
- **The user asked to remove the competitor's end image** and to make their own from the product page:
  a full-screen end card with the stars and customer count, NORRTVÄTT, the product photo, HÖSTREA,
  "4 PAKET –50 % · FRI FRAKT", a "SÄKRA ERBJUDANDET" button and the 30-day guarantee. Leave free space
  at y ≈ 0.75 for the captions.
- **Claims were adapted to the page:**
  - "Over two million pet owners" became "+15 000 kunder".
  - "Buy 2 get 2 free" became "4 paket till halva priset" (the 4-pack is 50 %).
  - "$9.99/box" became "20 kr per tablett".
  - The 60-day guarantee became the 30-day one.
  - "One tablet every two weeks" became "en tablett i månaden", since 12 tablets last a year.
  - The competitor's customer stories became generic advice, plus the real review from the page
    (Erika, two dogs).
  - Brand names (Afresh, OxiClean, Tide) became "vanliga maskinrengörare".
- Rendering 247 s at 720×1280 with 14 overlays and music took about 7 min, and splicing the source
  took 2 min. The full-quality file was 78 MB at crf 22, under GitHub's 100 MB limit.
