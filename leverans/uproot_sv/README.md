# Uproot-annonser gjorda 1:1 på svenska (Maskinrent)

Gjorda 2026-11-23. Fyra nya Uproot Clean-annonser (GitHub-releaserna `video48`, `video49`, `video50` och `video56`) gjorda om till
svenska Maskinrent-annonser. Det är inga iterationer: samma film, klipp, berättelse, ton och längd som Uproots original.
Auktoritet finns bara där originalet har den.

| Fil | Källa | Längd | Röst | Katalog |
|---|---|---|---|---|
| `Maskinrent video48 sv.mp4` | release `video48` | 0:49 | `tY9FLUZCUCQXwZYDwvWw` | B13 |
| `Maskinrent video49 sv.mp4` | release `video49` | 1:48 | `LzJuwbGODHbc1VvzbMrf` | B14 |
| `Maskinrent video50 sv.mp4` | release `video50` | 1:58 | `LzJuwbGODHbc1VvzbMrf` | B15 |
| `Maskinrent video56 sv.mp4` | release `video56` (4:5, 720x900) | 4:45 | `PLzKW5f9DmyCn5Vot26M` | B16 |

Varje film har en .srt med samma namn och ett manus i `manus/`. Manuset har den svenska meningen med starttid och Uproots
engelska original under.

## Vad som är ändrat
- **Manus.** Uproot → Maskinrent från Norrtvätt. Inga konkurrentnamn sägs, men deras kartonger syns kvar i filmen.
  Pro/Ultra är borttaget. Garantin är 30 dagar i stället för 60.
- **Röst.** ElevenLabs `eleven_v4` med `language_code: sv`. Manuset lästes i långa tagningar, en per stycke, som
  sedan delades i meningar. Varje mening ligger där den engelska meningen börjar. Tempot är högst 1,08 med atempo.
- **Text i bild.**
  - Uproots textremsor är borttagna med LaMa och ersatta med svenska vita textremsor i samma stil och på samma höjd,
    1-3 ord i Montserrat ExtraBold.
  - Där originalet har banner eller erbjudandegrafik i stället för textremsor finns inga textremsor hos oss heller.
- **Grafik på svenska.**
  - **video48:** bannern "Köp 2 få 2 GRATIS – REA / ENDAST 21 kr/rengöring / SLUTAR SNART!". Priset är
    999 kr / 48 tabletter.
  - **video49:**
    - märkena "Inget slipande" och "INGET FRÄTANDE / TVÄTTMASKIN";
    - erbjudandegrafiken "KÖP 2 / FÅ 2 / GRATIS", lastbilen "FRI FRAKT" och rutan "30 dagars pengarna tillbaka",
      med samma animation;
    - Uproots slutbild är ersatt med vår slutbild.
  - **video50:**
    - "SYRE- / BLEKMEDEL";
    - "AMYLAS", "PROTEAS" och "LIPAS";
    - de turkosa remsorna "KÖP 2 FÅ 2 GRATIS" och "+ FRI FRAKT";
    - Uproots slutbild är ersatt med vår slutbild. Den sista textremsan ligger i ett fritt band på slutbilden.
- **Slutbild.** NORRTVÄTT-loggan, två paket, "KÖP 2 · FÅ 2 PÅ KÖPET", 4,8/5, 15 000+ nöjda kunder, fri frakt,
  30 dagars pengarna tillbaka och norrtvatt.se.
- **Musik.** Nya ElevenLabs-bäddar (eleven_music_v2_5, instrumental), cirka 17 dB under rösten. Hela mixen är
  normaliserad till −15 LUFS. Musiken finns i flödena "Uproot → SV: video48–50 (Maskinrent)" och "Uproot → SV: video56
  (Maskinrent)".
- **video56:**
  - "Alfa-amylas", "Proteas" och "Lipas" i originalets stil.
  - Uproots recensionsbild (4:14–4:18, recensioner av en annan produkt) är ersatt med sex riktiga recensioner från
    norrtvatt.se, ordagrant (bara emojis borttagna).
  - Meningen om "the same people behind those famous pet hair removal tools" är borttagen; en tablett i månaden i
    stället för varannan vecka.
  - Texten togs bort med Vmake (SKM0002) och tre LaMa-pass för de vita kanter och streck Vmake lämnade (`vmake_remnants.py`, `vmake_lines.py`, `vmake_bars3.py`).
  - Vår slutbild i 4:5.

## Att tänka på
- Uproots, Affresh, Tide och OxiClean kartonger syns i filmen, som i originalet.
- video48 är 0,25 s längre än originalet: sista bilden står kvar så att sista ordet inte klipps.
- Verktygen finns i `leverans/underlag/uproot_sv/`.
