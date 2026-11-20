# Danmark – Nordvask Maskinren (shopnordvask.dk)

Danska versioner av alla sju historiska vinnare från den svenska butiken. Varje annons är samma annons som den
svenska (samma klipp, innehåll, erbjudande och upplägg). Bara språket är bytt till danska, och märket är Nordvask
Maskinren i stället för Norrtvätt Maskinrent.

Repo: `williamlind18/Admin`, branch `claude/funny-rubin-truuco`, mapp `leverans/danmark/`.

## Annonserna

| Svensk vinnare | Namn i Meta (förslag) | Video | Undertexter | Manus | Längd | Röst |
|---|---|---|---|---|---|---|
| b4 C2 | `DK b4 C2` | [mp4](nordvask_dk_b4-C2_da.mp4) | [srt](nordvask_dk_b4-C2_da.srt) | [manus](manus/manus_b4-C2_da.txt) | 3:48 | dansk man 40–50 år |
| b1 C3 | `DK b1 C3` | [mp4](nordvask_dk_b1-C3_da.mp4) | [srt](nordvask_dk_b1-C3_da.srt) | [manus](manus/manus_b1-C3_da.txt) | 4:49 | dansk man 40–50 år |
| b3.1 C8 | `DK b3.1 C8` | [mp4](nordvask_dk_b3.1-C8_da.mp4) | [srt](nordvask_dk_b3.1-C8_da.srt) | [manus](manus/manus_b3.1-C8_da.txt) | 3:42 | dansk man 40–50 år |
| b3 C3 | `DK b3 C3` | [mp4](nordvask_dk_b3-C3_da.mp4) | [srt](nordvask_dk_b3-C3_da.srt) | [manus](manus/manus_b3-C3_da.txt) | 4:23 | dansk man 40–50 år |
| b5 C2 | `DK b5 C2` | [mp4](nordvask_dk_b5-C2_da.mp4) | [srt](nordvask_dk_b5-C2_da.srt) | [manus](manus/manus_b5-C2_da.txt) | 3:30 | dansk man 40–50 år |
| b5.1 C3 | `DK b5.1 C3` | [mp4](nordvask_dk_b5.1-C3_da.mp4) | [srt](nordvask_dk_b5.1-C3_da.srt) | [manus](manus/manus_b5.1-C3_da.txt) | 3:51 | dansk kvinna 30–40 år |
| b5 C5 | `DK b5 C5` | [mp4](nordvask_dk_b5-C5_da.mp4) | [srt](nordvask_dk_b5-C5_da.srt) | [manus](manus/manus_b5-C5_da.txt) | 0:53 | dansk kvinna 40–50 år |

Erbjudandet är detsamma som i Sverige och Norge, i DKK: köp två, få två på köpet (fire pakker til prisen for to),
999 kroner för fyra paket, fri frakt och 30 dagars pengarna-tillbaka-garanti. Länken ska gå till shopnordvask.dk.

## Hur de är gjorda

- **Källa:** de svenska annonserna, kontrollerade mot de som körs i Meta (längd och innehåll stämmer). b1 C3 i Meta har
  ett musikspår som inte fanns i vår källfil. Musiken togs ur Meta-versionen, så den danska b1 C3 låter som den live.
- **Svensk text borttagen** med Vmake (borttagning av undertexter). De svenska FÖRE/EFTER-skyltarna i b5 C2 (2:41–2:44)
  är ersatta med FØR/EFTER i samma vita rutor.
- **Röst:** ElevenLabs `eleven_v4` med språkkod `da`, rösterna du valde. Ett stycke på 5–8 meningar per tagning,
  uppdelat i meningar.
- **Tajming:** varje dansk mening börjar där den svenska började, så rösten följer samma klipp. Danskan är 5–20 %
  kortare än svenskan. För att slippa långa pauser är rösten något nedsaxad (atempo 0,92–0,94) där det behövs, och
  uppsnabbad som mest ×1,08. Pauserna ligger oftast på 0,4–0,8 s.
- **Musik och ljud:** samma musik som i den svenska annonsen, i samma läge och med samma nivå mot rösten. Ljudstyrkan
  är matchad mot den svenska (cirka −15 LUFS).
- **Undertexter:** 1–3 ord i Montserrat ExtraBold, på samma höjd som de svenska. Belopp och större tal står som
  siffror (999 kroner, 50 %, 15.000 kunder, 30 dage).
- **Slutbilder:** b5 C2 slutar med Nordvask-produktbilden i stället för den svenska Maskinrent-bilden. b5.1 C3 har
  en dansk slutbild (4,8 ud af 5, +15.000 kunder, UDSALG, 4 PAKKER –50 %, FRI FRAGT, SIKR DIG TILBUDDET).

## Lanseringsannonserna (de 26 från Norge)

Samma 26 videor som i den norska kampanjen "CBO - Norrtvätt NO" (Ad account 3). A1 C1, A1 C2 och A1 C3 finns redan
ovan (b1 C3, b3 C3 och b3.1 C8). Resten görs i omgångar om fem, i ordning efter hur mycket de spenderat i Norge.

| Meta | Annons | Video | Undertexter | Manus | Längd | Röst |
|---|---|---|---|---|---|---|
| A5 C4 | video30, NASA-enzymer | [mp4](nordvask_dk_A5-C4_da.mp4) | [srt](nordvask_dk_A5-C4_da.srt) | [manus](manus/manus_A5-C4_da.txt) | 4:08 | dansk man 40–50 år |
| A5 C5 | video33, servicetekniker | [mp4](nordvask_dk_A5-C5_da.mp4) | [srt](nordvask_dk_A5-C5_da.srt) | [manus](manus/manus_A5-C5_da.txt) | 6:39 | dansk man 40–50 år |
| A3 C1 | video5 | [mp4](nordvask_dk_A3-C1_da.mp4) | [srt](nordvask_dk_A3-C1_da.srt) | [manus](manus/manus_A3-C1_da.txt) | 4:05 | dansk kvinna 30–40 år |
| A5 C1 | video31 | [mp4](nordvask_dk_A5-C1_da.mp4) | [srt](nordvask_dk_A5-C1_da.srt) | [manus](manus/manus_A5-C1_da.txt) | 4:29 | dansk man 40–50 år |
| A1 C4 | Maskinrent 4, biofilm | [mp4](nordvask_dk_A1-C4_da.mp4) | [srt](nordvask_dk_A1-C4_da.srt) | [manus](manus/manus_A1-C4_da.txt) | 5:13 | dansk man 40–50 år |
| A4 C5 | Maskinrent 5, tre misstag | [mp4](nordvask_dk_A4-C5_da.mp4) | [srt](nordvask_dk_A4-C5_da.srt) | [manus](manus/manus_A4-C5_da.txt) | 2:16 | dansk man 40–50 år |
| A2 C5 | video25, rean slutar idag (4:5) | [mp4](nordvask_dk_A2-C5_da.mp4) | [srt](nordvask_dk_A2-C5_da.srt) | [manus](manus/manus_A2-C5_da.txt) | 0:20 | dansk kvinna 40–50 år |
| A4 C4 | Maskinrent 8 | [mp4](nordvask_dk_A4-C4_da.mp4) | [srt](nordvask_dk_A4-C4_da.srt) | [manus](manus/manus_A4-C4_da.txt) | 1:02 | dansk kvinna 40–50 år |
| A3 C2 | Maskinrent 4 | [mp4](nordvask_dk_A3-C2_da.mp4) | [srt](nordvask_dk_A3-C2_da.srt) | [manus](manus/manus_A3-C2_da.txt) | 4:09 | dansk kvinna 40–50 år |
| A3 C3 | Maskinrent 3, 4-minutersversionen | [mp4](nordvask_dk_A3-C3_da.mp4) | [srt](nordvask_dk_A3-C3_da.srt) | [manus](manus/manus_A3-C3_da.txt) | 4:00 | dansk kvinna 40–50 år |

Omgång 2 (A4 C5, A4 C4, A3 C2, A3 C3) är byggd på originalfilmerna i GitHub-releaserna (video17, video18, video10,
video6), som är samma klipp utan svensk text. Bara det den svenska versionen lade till är gjort om på danska:
15.000 TILFREDSE KUNDER, FRI FRAGT, UDSALGET SLUTTER SNART och 30 DAGES PENGENE TILBAGE. Den svenska "Lipas"-etiketten
i A4 C5 behövs inte, för originalets "Lipase" är redan rätt på danska. A2 C5 har rubriken NORDVASK / 2-PAK −40 % /
SIDSTE CHANCE / KUN 25 KR/TABLET. Dess 9:16-version finns bara i Meta och görs separat.

Alla svenska texter i bild är bytta mot danska på samma plats och i samma stil: skyltar (SEBUM/HUNDENS HUDFEDT,
DYREHÅR = PROTEIN, SEBUM = FEDT, Alfa-amylase/Protease/Lipase, AFKALKER MASKINEN, PASSER TIL ALLE VASKEMASKINER,
SIKKER FOR AFLØB, Iltblegemiddel på ingredienslistorna), CNN-rubriken (FORSKERE SKABER "SUPERENZYM"), sms:et,
erbjudandekorten (UDSALG, 4 PAKKER –50 %, 20 KR / TABLET, HOLDER I 4 ÅR, FRI FRAGT), garantiremsorna (PENGENE
TILBAGE I 30 DAGE) och slutbilderna (NORDVASK, 4,8 ud af 5, +15.000 kunder, SIKR DIG TILBUDDET).

## Att tänka på

- **Förpackningen på produktbilden är den norska** (Nordvask Maskinren, "rengjøringstabletter", "utviklet for
  dyreeiere"). Logga och produktnamn är desamma i Danmark, men småtexten på asken är norsk. Finns en dansk
  produktbild kan den bytas in i b5 C2 och b5.1 C3.
- Uproot-förpackningarna i klippen är kvar, precis som i de svenska annonserna.
- Påståendena är desamma som i de svenska annonserna (bland annat 15.000 kunder och 4,8 av 5, tekniker-berättelserna
  och NASA-enzymerna). Kontrollera att de gäller för den danska butiken innan annonserna går live.
