# Norska versioner: gäller bara de här fyra annonserna

När användaren skriver **"gör alla annonser på norska"** (eller något liknande) ska exakt de fyra
annonserna nedan göras på norska. De gjordes i sessionen 2026-09-29–2026-10-14.

- **Ingår inte:** svenska annonser som görs efter 2026-10-14.
- **Ingår inte heller:** de äldre Maskinrent-videorna i `leverans/` (`norrtvatt_maskinrent_sv.mp4`,
  `norrtvatt_maskinrent2_sv.mp4`).
- **Undantag:** en annons utanför listan görs bara på norska om användaren uttryckligen nämner den.

De norska versionerna ska vara **samma annonser, bara på norska**:

- Samma klipp och bildredigering.
- Samma musik.
- Samma synkpunkter.
- Samma vita rutor och captions-stil, med norsk text.

## De fyra annonserna

| # | Annons | Original (GitHub-release) | Svensk leverans | Svenskt manus | Svensk röst | ElevenLabs-flöde |
|---|---|---|---|---|---|---|
| 1 | **Video 5**: "Tre ingredienser som saknas", kvinnans berättelse med hundfilten, 4:04,6 | `video5` / `norrtvatt.claude.-.1.3.mp4` | `leverans/norrtvatt_video5_sv.mp4` + `.srt` | `leverans/manus_video5.txt` | `p47LfPZdd7LXERMMfx1R` "30 år kvinna" | `vLNA1dAvAtNIy7syqSd1` |
| 2 | **Video 11**: reparatören och NASA-tricket, 4:22,7 | `video11` / `Norrtvatt.trimmad.-.C3.mp4` | `leverans/norrtvatt_video11_sv.mp4` + `.srt` | `leverans/manus_video11.txt` | `OvO33bxTqNfwQfoR6mVh` "Äldre man 50-60 år - SE" | `0FLyyvGyKCMBzNJkuZKV` |
| 3 | **Video 14**: "Kolonin, 200 dagar i tvättmaskinen" (animerad), 1:24,9 | `video14` / `norrtvatt_-_konkurrent_6.mp4` | `leverans/norrtvatt_video14_sv.mp4` + `.srt` | `leverans/manus_video14.txt` | `UkRAtFubBAJ0Ggc3W2XX` "Man mörk röst - SE" | `XgWWVgjvLiVHrxzFzb0W` |
| 4 | **Video 15**: reparatörens "tre anledningar", 2:00,4 | `video15` / `Norrtvatt.trimmad.-.C5.mp4` | `leverans/norrtvatt_video15_sv.mp4` + `.srt` | `leverans/manus_video15.txt` | `OvO33bxTqNfwQfoR6mVh` "Äldre man 50-60 år - SE" | `AImwBgwLPGKlGiJpFlrb` |

Manusfilerna börjar med 2–3 rubrikrader. Radnumren nedan räknas från första manusraden.

## Så görs de norska versionerna

1. **Fråga i ett enda meddelande:**
   - Norsk röst-ID för varje annons, eller samma röst för alla.
   - Norska produktfakta: produkt- och varumärkesnamn i Norge, pris och erbjudande i NOK, antal
     garantidagar, frakt, antal kunder och webbadress.
   - Om musiken ska vara densamma (standard: ja).
2. **Footage:** kör `bash leverans/norska/rebuild_sources.sh WORKDIR` (eller med bara vissa nummer,
   t.ex. `... WORKDIR 15`). Skriptet återskapar exakt den redigerade video som den svenska versionen
   byggdes på:
   - **Video 5:** kartan över Florida bortklippt.
   - **Video 14:** uppskalad till 1080×1872.
   - **Video 15:** 60-dagarstexten borttagen och den suddiga "3 REASONS"-bilden ersatt.
3. **Manus:** översätt det svenska manuset **rad för rad** till naturlig norsk bokmål, med samma antal
   rader. Då gäller synkpunkterna nedan oförändrade. Byt pris, erbjudande och fakta till de norska.
   Visa manuset för godkännande innan några credits används.
4. **Röst:** följ `.claude/skills/ad-video-localizer/references/elevenlabs.md`:
   - eleven_v3, en inläsning i ett svep.
   - `language_code` för norska (kontrollera koden mot modellschemat).
   - Taggen `[confident]` i början och sparsamt med kommatecken.
   - Tre inläsningar, välj den bästa med `scripts/score_takes.py`.
   - Aldrig nedsaktning, bara atempo-uppsnabbning på högst cirka 1,08.
5. **Musik:** återanvänd `leverans/norska/videoN/music.mp3` med `--bed-db -16`.
6. **Rutor:** samma tider och positioner som i `videoN/labels_sv.txt`, med norsk text (se tabellen nedan).
   Bygg dem med `chunk_captions.py --label`.
7. **Leverans:**
   - Filer: `leverans/norrtvatt_videoN_no.mp4` + `.srt` + `leverans/manus_videoN_no.txt`.
   - Filer över 100 MB komprimeras i två pass till cirka 95 MB.
   - Förhandsvisning i chatten.

## Synkpunkter (radnummer i manuset)

Använd med `plan_timeline.py SENT --video-duration D`.

- **Video 5** (D = 244.57):
  `--anchor 10:start=31.5-33.2 --anchor 30:start=98.3-100.1 --anchor 33:start=109.0-110.6
  --anchor 36:start=123.0-124.2 --anchor 39:start=136.3-137.0 --anchor 41:start=139.6-140.4
  --anchor 44:start=152.0-153.3 --anchor 47:start=168.9-170.8 --anchor 54:end=196.4-197.8
  --anchor 63:start=219.5-220.5`
- **Video 11** (D = 262.69):
  `--anchor 3:start=9.0-12.0 --anchor 6:start=17.5-20.5 --anchor 8:start=29.5-31.5
  --anchor 11:start=44.8-46.0 --anchor 14:start=53.8-55.4 --anchor 17:start=67.0-68.5
  --anchor 19:start=70.5-71.5 --anchor 21:start=73.8-75.8 --anchor 26:start=92.5-96.0
  --anchor 30:start=109.4-111.2 --anchor 33:start=121.5-123.4 --anchor 37:start=138.7-140.5
  --anchor 38:start=143.4-145.2 --anchor 41:start=160.0-162.5 --anchor 42:start=168.0-170.0
  --anchor 44:start=177.5-179.5 --anchor 45:start=184.5-186.5 --anchor 47:start=191.0-192.3
  --anchor 50:start=203.8-205.5 --anchor 55:start=224.0-226.0 --anchor 59:start=247.0-249.0`
- **Video 14** (D = 84.93):
  `--anchor 2:start=4.7-5.4 --anchor 4:start=7.4-9.6 --anchor 7:start=14.4-16.0
  --anchor 8:start=17.2-19.2 --anchor 9:start=23.0-23.8 --anchor 11:start=24.6-25.6
  --anchor 13:start=28.0-28.8 --anchor 15:start=37.2-37.8 --anchor 16:start=39.2-39.8
  --anchor 17:start=40.6-41.2 --anchor 18:start=43.3-44.0 --anchor 22:start=54.6-56.0
  --anchor 25:start=61.0-63.6 --anchor 26:start=64.3-65.5 --anchor 28:start=70.8-71.4
  --anchor 32:start=79.3-80.0`
- **Video 15** (D = 120.37):
  `--anchor 5:start=17.8-18.2 --anchor 11:start=43.8-46.4 --anchor 12:start=47.4-50.0
  --anchor 16:start=66.6-68.6 --anchor 17:start=73.0-75.0 --anchor 21:start=86.5-87.6
  --anchor 22:start=91.0-92.0 --anchor 23:start=97.2-98.4 --anchor 25:start=104.6-105.8
  --anchor 26:start=108.3-109.0 --anchor 27:start=112.4-113.4`

## Rutor med text som ska bli norsk

| Video | Tid | Svensk text | Förslag på norska (kontrollera med användaren) |
|---|---|---|---|
| 5 | 3:56,8–3:58,8 | SÄKER FÖR AVLOPP (över "SEPTIC SAFE") | TRYGG FOR AVLØP |
| 5 | 2:01,4 | tom vit ruta (över "every load,") | oförändrad |
| 15 | 0:45,0–0:46,1 och 1:07,4–1:07,8 | 3 ANLEDNINGAR (över "3 REASONS") | 3 GRUNNER |
| 15 | 1:31,5–1:37,8 | 15 000+ KUNDER (över kundräknaren) | 15 000+ KUNDER (eller det norska antalet) |
| 15 | 1:47,5–1:48,3 | 30 DAGARS / PENGARNA TILLBAKA | 30 DAGERS / PENGENE TILBAKE |
| 15 | 1:51,2–1:52,6 | FRI FRAKT (följer lastbilen bild för bild) | GRATIS FRAKT |

Videorna 11 och 14 har inga rutor.
