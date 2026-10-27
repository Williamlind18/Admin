# Lista 1: annonser som ska göras på norska (låst 2026-10-27)

När användaren skriver **"gör alla annonser på norska"** betyder "alla annonser" **exakt annonserna i den här listan**,
inget annat. Annonser som skapas efter 2026-10-27 (även i samma session och även på svenska) hör **inte** hit.
Lägg nya annonser i en annan mapp under `annonser/` och lägg aldrig till något i den här listan utan att användaren ber om det.

Norska versioner ska vara **samma annonser**: samma bild, layout, erbjudande och upplägg. Bara språket byts
(norsk text i bilden, norsk primary text och rubrik). Valuta, priser, slutdatum och "fri frakt" följer det norska
erbjudandet om användaren anger ett. Annars frågar man en gång innan man bygger.

## Bildannonser (21 st), svenska original i `se/`

| Id | Fil | Vad |
|---|---|---|
| K1 | `se/K1_3enzymer.jpg` | Konkurrentbild översatt: 3 enzymer, kort, klistermärke, Norrtvätts kartong |
| K2 | `se/K2_sista_chansen_kartonger.jpg` | Konkurrentbild översatt: Sista chansen, 21 kr/tablett, två kartonger |
| K3 | `se/K3_fore_efter_tablett.jpg` | Konkurrentbild översatt: före/efter + tablett, orange cirkel (vinnarkonceptet) |
| K4 | `se/K4_fore_efter_banner.jpg` | Konkurrentbild översatt: före/efter, kartong, lila banner |
| A1 | `se/A1_betyg.jpg` | Vinnarbilden: 4,8/5 från 1 046 recensioner |
| A2 | `se/A2_garanti.jpg` | Vinnarbilden: prova 30 dagar riskfritt |
| A3 | `se/A3_gummilist.jpg` | Vinnarupplägget på gummilist före/efter |
| A4 | `se/A4_trumma_manad.jpg` | Vinnarupplägget på trumma före/efter: från 21 kr per månad |
| A5 | `se/A5_recensioner.jpg` | Recensioner + 4,8/5 + erbjudande |
| A6 | `se/A6_paket.jpg` | Välj ditt paket: 4 paket med priser och ordinarie priser |
| A7 | `se/A7_utan_med.jpg` | Utan vs. med Maskinrent |
| B1 | `se/B1_brev_4x5.png` | BOF: Brevet, "Nu säger vi farväl" |
| B2 | `se/B2_rea_4x5.png` | BOF: Rea-skylten på lagerpall, "Upp till 50% / Sista chansen" |
| B3 | `se/B3_postit_4x5.png` | BOF: Post-it-lappar på köksbord bredvid kartongen |
| B4 | `se/B4_hejda_4x5.png` | BOF: "Vi säger hejdå" |
| B5 | `se/B5_kvitto_4x5.png` | BOF: Kvittot, 2-pack 619 kr, du sparar 379 kr |
| B6 | `se/B6_trappan_4x5.png` | BOF: Rabatt-trappan, kr per tablett |
| B7 | `se/B7_kalender_1x1.png` | BOF: Kalendern, söndag 18 inringad (enda annonsen med datum) |
| B8 | `se/B8_stampel_1x1.png` | BOF: Stämpeln på produktbilden |
| B9 | `se/B9_kupong_4x5.png` | BOF: Kupongen "Klipp till!" |
| B10 | `se/B10_prisskylt_4x5.png` | BOF: Gul prisskylt i butikshylla, 2-pack 619:- |

Slutversionerna gäller: B1–B10 med "avslutas ikväll 23:59" och utan 999 kr (utom B7, kalendern),
och B3 är köksbordsversionen.

## Copy
- `copy/A_K_copy.md`: T1 (översatt konkurrent-copy, bara text), all bildtext i K1–K4 och A1–A7, primary text och rubriker för A.
- `copy/B_copy_bof.md`: primary text + rubrik för B1–B10.
- `copy/B_pastaenden.md`: påståenden som måste stämma i butiken.

## Video (1 st)
| Id | Fil | Vad |
|---|---|---|
| V1 | `../../leverans/norrtvatt_maskinrent2_sv.mp4` (+ `.srt`, `manus_maskinrent2.txt`) | Maskinrent video 2, svensk voiceover och captions |

En norsk V1 kräver en ny röstinläsning. Följ `ad-video-localizer` och fråga efter röst-ID.
Video 1 (`norrtvatt_maskinrent_sv.mp4`) gjordes i en tidigare session och ingår inte.

## Bygga om på norska
Källorna finns i `kalla/`:
- `tools/`: alla skript. K1–K4: `compose4–7.py`. A1–A7: `winner_remix.py`, `ad_split.py`, `ad_reviews.py`,
  `ad_packages.py`, `ad_compare.py` med `adlib.py` och `boxlib.py`. B1–B4: `render.py` + `specar/annonser.json`.
  B3: `note_text.py` + `specar/notes_postit.json`. B5–B9: `html_ads.py` + `specar/nya.py`. B10: `warp_html.py` + `specar/skylt.json`.
  `chrome.sh` kör Chromium headless med `--no-sandbox`.
- `bilder/`: konkurrentoriginalen, produktbilderna (riktiga Shopify-bilder och frilagd kartong) och miljöbilderna.
  Miljöbilderna är sparade som JPEG.
- `fonts_ttf/` (Pillow) och `fonts_web/` (lokal Google Fonts-CSS för Chrome).

Skripten och specarna pekar på sökvägar i den gamla sessionens scratchpad. Peka om dem till `kalla/` innan de körs.
All text sätts i HTML eller Pillow, aldrig av en bildmodell.
