# Annonser som ska göras på norska

När användaren skriver **"gör alla annonser på norska"** gäller det **bara annonserna i listan nedan**.
Listan är låst sedan 2026-10-27. Nya svenska annonser som görs efter det ska **inte** läggas till här
och **inte** göras på norska, om inte användaren uttryckligen ber om det för en viss annons.

Den norska versionen ska vara samma annons: samma video, samma upplägg och samma innehåll, bara på
naturlig norska (bokmål). Följ `.claude/skills/ad-video-localizer/SKILL.md` som vanligt.

## Listan

### 1. Maskinrent-video 3 (gjord 2026-09-29)
- **Källvideo:** GitHub-release `video3`, filen `norrtvatt.claude.1.1.mp4`
  (30 s, 1080×1332, sha1 `63a8c258eba75a00c6bfef3289cd5761b5f93940`).
  Originalet är en engelsk Uproot-annons.
- **Svensk leverans:** `leverans/norrtvatt_maskinrent3_sv.mp4`, `.srt` och manuset
  `leverans/manus_maskinrent3.txt`.
- **Upplägg:** tio meningar i en enda eleven_v3-tagning. Ett ankare: mening 6 (NASA-raden) börjar vid
  16,3-17,0 s, där mikroskopet och sedan astronauten syns. Användaren ville ha kvar "NASA".
- **Slutruta** från början av "Har du husdjur…" (cirka 26,0 s) till slutet: produktbilden och en vit
  ruta med svart text, "HÖSTREA / Upp till 50 % rabatt". Gjord med `make_endcard.py` och
  `render.py --overlay`.
  - Produktbilden finns i `leverans/underlag/maskinrent_produktbild_sv.png`. Kartongen har svensk
    text, så fråga om det finns en norsk produktbild.
  - Rutans text översätts.
- **Captions:** de handvalda svenska bitarna finns i `leverans/underlag/maskinrent3_captions_sv.txt`
  som förebild.
- **Uproots kartong får synas** (användarens beslut). Ingen musik, eftersom användaren lägger på den själv.

## Att fråga om innan den norska versionen görs
- Röst-ID för norska (fråga alltid).
- Norska priser, erbjudande och rea (NOK) och den norska produktsidan eller skärmdumpar. Slutrutans
  erbjudande måste stämma med den norska sidan.
- Om det finns en norsk produktbild till slutrutan.
