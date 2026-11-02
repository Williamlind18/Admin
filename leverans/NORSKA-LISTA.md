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
- **Norsk version KLAR (2026-11-02):** `leverans/nordvask_maskinren3_no.mp4`, `.srt` och
  `leverans/manus_maskinren3_no.txt`. I Norge heter varumärket **NORDVASK** och produkten **MASKINREN**
  (samma erbjudanden som i Sverige). Röst-ID wmWNq8zv8Au6slnVf0MZ (kvinna, norska), eleven_v4 med
  `language_code: no`. Norsk kartong: `leverans/underlag/maskinren_produktbild_no.png`. Slutruta
  "SALG / Opptil 50 % rabatt". Captions: `leverans/underlag/maskinren3_captions_no.txt`.

## Att fråga om innan den norska versionen görs
- Röst-ID för norska (fråga alltid).
- Norska priser, erbjudande och rea (NOK) och den norska produktsidan eller skärmdumpar. Slutrutans
  erbjudande måste stämma med den norska sidan.
- Om det finns en norsk produktbild till slutrutan.

## Uttryckligen beställda efter låsningen
- **2026-11-02:** användaren bad uttryckligen om norska versioner av **video25, video30 och video33**
  (de som gjordes i samma session efter att listan låstes). Manusutkast:
  `leverans/underlag/norska_manus_25_30_33_utkast.txt`. Varumärket heter NORDVASK, produkten MASKINREN,
  samma erbjudanden som i Sverige, "salg" i stället för "rea". Nyare annonser än så ingår fortfarande inte.
- **Status 2026-11-02:**
  - video25 KLAR: `leverans/nordvask_video25_salget_slutter_no.mp4` (+ .srt, `manus_video25_salget_slutter_no.txt`).
    Röst wmWNq8zv8Au6slnVf0MZ (kvinna), Vmake-rensad (SKM0003).
  - video33 KLAR: `leverans/nordvask_video33_servicetekniker_no.mp4` (+ .srt, `manus_video33_servicetekniker_no.txt`).
    Röst iWsqLB1KXhKYZqry79ma (man), gratis textborttagning (burned_captions + patch_cut), samma klipp och
    musik som den svenska. Bara ALFA-AMYLASE täcks; PROTEASE och LIPASE stavas lika på norska.
  - video30 KLAR: `leverans/nordvask_video30_nasa_enzymer_no.mp4` (+ .srt, `manus_video30_nasa_enzymer_no.txt`).
    Röst iWsqLB1KXhKYZqry79ma (man), Vmake-rensad (SKM0003), samma skarvar, kort, musik och textrutetider
    som den svenska (tiderna togs fram genom att jämföra den svenska filen med Vmake-videon bildruta för bildruta).
