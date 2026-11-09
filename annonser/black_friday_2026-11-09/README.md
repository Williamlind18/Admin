# Black Friday BOF: 10 bildannonser (2026-11-09)

**Ingår INTE i lista 1** (`../lista1_2026-10-27/`, "gör alla annonser på norska").

Erbjudandet är samma som nu men heter Black Friday: upp till 50 % rabatt, köp 2 – spara 379 kr (2-pack 619 kr, ord. 998 kr), fri frakt, 30 dagars pengarna-tillbaka och "avslutas ikväll 23:59". Annonserna har inga datum och visar aldrig 999 kr. Ordet "höstrea" förekommer inte.

Alla annonser är 4:5 (1080×1350). Copy finns i `copy/copy_bf.md` och påståenden i `copy/pastaenden.md`. Översikt: `oversikt_BF01-10.jpg`.

| Id | Fil | Etikett | Koncept | Bygger på |
|---|---|---|---|---|
| BF_01 | `se/BF_01_kvittot_4x5.png` | MA_bf50_kvitto_v1 | Black Friday-kvitto på svart, "Du sparar 379 kr" inringat | vinnaren Kvittot (C6) |
| BF_02 | `se/BF_02_kvittot_foto_4x5.png` | MA_bf50_kvittofoto_v1 | Kvitto i handen framför tvättmaskinen + svart kort "upp till 50 %" | vinnaren Kvittot (C6) |
| BF_03 | `se/BF_03_21kr_tablett_4x5.png` | MA_bf50_21kr_v1 | "Black Friday – från 21 kr/tablett", svävande tabletter, fri frakt | vinnaren C3-ny |
| BF_04 | `se/BF_04_black_friday_4x5.png` | MA_bf50_blackfriday_v1 | BLACK / kartong / FRIDAY, "sista kvällen", klistermärke 50 % | vinnaren Hejdå (C8) |
| BF_05 | `se/BF_05_bokstavstavla_4x5.png` | MA_bf50_tavla_v1 | Bokstavstavla med plastbokstäver och kartongen bredvid | Aktivnords whiteboard |
| BF_06 | `se/BF_06_kassen_4x5.png` | MA_bf50_kasse_v1 | Svart shoppingkasse, hänglapp "Black Friday 50 %" | nytt |
| BF_07 | `se/BF_07_neon_4x5.png` | MA_bf50_neon_v1 | Neonskylt "BLACK FRIDAY / UPP TILL 50 %" i mörk tvättstuga | nytt |
| BF_08 | `se/BF_08_avsparrning_4x5.png` | MA_bf50_avsparrning_v1 | Gul-svart avspärrningstejp över mörk produktbild | nytt |
| BF_09 | `se/BF_09_paketet_4x5.png` | MA_bf50_paket_v1 | Två kartonger med svart rosett, "2 för 619 kr" | nytt |
| BF_10 | `se/BF_10_vanlig_fredag_4x5.png` | MA_bf50_vanligfredag_v1 | "En vanlig fredag 998 kr" mot "Black Friday 619 kr" | nytt |

Alla tio klarar BOF-testet: tar man bort erbjudandet finns ingen annons kvar.

## Källor (`kalla/`)
- `bilder/*_ai.jpg`: rå AI-miljöer.
- `bilder/*_bas.jpg`: efter fix, alltså riktig kartongfront plus text på lapp, tavla, kvitto och neon, före rubrikerna.
- `tools/`: samma verktyg som i `../bof_omgang4_2026-11-09/`, med några tillägg:
  - `paste_face.py` har fått `--keep-dark` (band och kasse framför kartongen), `--clip-y` och `--exclude` (för en andra kartong).
  - `warp_html.py` har fått `blend: "screen"` för neon.
- `specar/`: en spec per annons. Sökvägarna pekar på sessionens scratchpad. Peka om dem till `kalla/bilder/` innan de körs.
