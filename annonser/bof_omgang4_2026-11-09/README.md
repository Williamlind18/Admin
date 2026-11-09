# BOF omgång 4: 6 nya bildannonser (2026-11-09)

**Ingår INTE i lista 1.** Lista 1 (`../lista1_2026-10-27/`) är listan för "gör alla annonser på norska". Annonserna här är skapade efter 2026-10-27 och ska inte översättas när användaren skriver det.

Alla är 4:5 (1080×1350). Ingen 9:16. Copy finns i `copy/copy_bof.md` och påståenden i `copy/pastaenden.md`. Översikt: `oversikt_SE18-23.jpg`.

| Id | Fil | Etikett | Koncept | Bygger på |
|---|---|---|---|---|
| SE_18 | `se/SE_18_ikvall_imorgon_4x5.png` | MA_rea50_ikvallimorgon_v1 | Ikväll 619 kr vs imorgon 998 kr, delad bild | vinnarens "spara 379 kr" |
| SE_19 | `se/SE_19_klockan_4x5.png` | MA_rea50_klocka_v1 | Väckarklocka som visar 23:59 i köket på kvällen | nytt brådske-koncept |
| SE_20 | `se/SE_20_kalkylatorn_4x5.png` | MA_rea50_kalkylator_v1 | Kalkylator som visar 379, "Köp 2 och spara 379 kr" | vinnarens "spara 379 kr" |
| SE_21 | `se/SE_21_kvittot_foto_4x5.png` | MA_rea50_kvitto_v2 | Riktigt kvitto på tvättmaskinen, "Du sparar 379 kr" inringat | iteration av vinnaren B5 (C6) |
| SE_22 | `se/SE_22_notisen_4x5.png` | MA_rea50_notis_v1 | Låsskärm 21:47 med två notiser från Norrtvätt | påminnelse + spara 379 kr |
| SE_23 | `se/SE_23_reatejp_4x5.png` | MA_rea50_reatejp_v1 | Kartong med röd rea-tejp på lagerhylla, "Sista kvällen på höstrean" | nytt brådske-koncept |

Alla sex klarar BOF-testet: tar man bort erbjudandet finns ingen annons kvar.

## Källor (`kalla/`)
- `bilder/*_ai.jpg`: rå AI-miljöer (Higgsfield nano_banana_2_1, kartongen som referens).
- `bilder/*_bas.jpg`: miljön efter fix, alltså riktig kartongfront inklistrad och text satt på klocka, kalkylator, kvitto och tejp, före rubrikerna.
- `tools/paste_face.py`: hittar kartongfronten med SIFT och klistrar in den riktiga fronten i bildens ljus. Flaggor: `--teal` och `--top=`.
- `tools/warp_html.py`: sätter HTML-text i perspektiv på ett objekt. Har `clip` och `blend` (multiply för tryck, over för skärmar).
- `tools/tape.py`: rea-tejpen.
- `tools/seg7.py`: sjusegmentssiffror.
- `tools/html_ads.py`: slutrendering.
- `tools/grid.py` och `tools/findquad.py`: hjälp för att mäta hörn.
- `specar/`: en spec per annons.

Sökvägarna i specarna pekar på sessionens scratchpad (`../ai/`, `../work/`). Peka om dem till `kalla/bilder/` innan de körs. `chrome.sh` pekar på Chromium headless shell 1243.
