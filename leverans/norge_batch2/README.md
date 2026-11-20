# NO batch 2: norska versioner av sju svenska annonser (Nordvask Maskinren)

Gjorda 2026-11-20. Samma annonser som de svenska, bara på norska:

- NORDVASK i stället för NORRTVÄTT och MASKINREN i stället för MASKINRENT.
- Samma erbjudanden, i NOK.
- Samma bild, musik och textposition.
- Rösten matchar den svenska i kön.

| NO batch 2 | Svensk källfil (användarens namn) | Svensk annons, Meta-id | Svensk leverans (sökväg @ gren) | Längd | Norsk röst |
|---|---|---|---|---|---|
| `Norrtvätt NO batch 2 - C1.mp4` | Norrtvätt ny batch 4 - C3.mp4 | b4 C2, 3819724594858787 | `leverans/norrtvatt_video22_sv.mp4` @ `claude/quirky-mayer-tsglxb` | 3:47.7 | Norsk äldre man 55-60 år |
| `Norrtvätt NO batch 2 - C2.mp4` | ny batch 6 – C4 H1 (I1 av b3 C3).mp4 | b6 C4 H1, 1113564634640493 | `leverans/batch6/nb6_C4_H1_I1-b3C3_sv.mp4` @ `claude/funny-rubin-truuco` | 3:05.5 | Norsk äldre man 55-60 år |
| `Norrtvätt NO batch 2 - C3.mp4` | Norrtvätt ny batch 5 - C2.mp4 | b5 C2, 1082218854817791 | `leverans/norrtvatt_vsl_reparator.mp4` @ `claude/video-editing-15noqg` | 3:30.0 | Norsk äldre man 55-60 år |
| `Norrtvätt NO batch 2 - C4.mp4` | Norrtvätt ny batch 5 - C9.mp4 | b5.1 C3, 4567448416836030 | `leverans/norrtvatt_video43_tre_enzymer_sv.mp4` @ `claude/focused-hamilton-930j6d` | 3:50.5 | medelålders kvinna - NO |
| `Norrtvätt NO batch 2 - C5.mp4` | ny batch 6 – C3 H3 (I1 av b3.1 C8).mp4 | b6 C3 H3, 1485398660188382 | `leverans/batch6/nb6_C3_H3_I1-b3.1C8_sv.mp4` @ `claude/funny-rubin-truuco` | 3:09.1 | Norsk äldre man 55-60 år |
| `Norrtvätt NO batch 2 - C6.mp4` | Norrtvätt ny batch 5 - C5.mp4 | b5 C5, 2303657343808622 | `leverans/norrtvatt_maskinrent9_enzymer_sv.mp4` @ `claude/funny-rubin-truuco` | 0:52.7 | medelålders kvinna - NO |
| `Norrtvätt NO batch 2 - C7.mp4` | Norrtvätt ny batch 5 - C6.mp4 | b5 C6, 1451208423003504 | `leverans/norrtvatt_video39_sv.mp4` @ `claude/quirky-mayer-tsglxb` | 1:48.6 | medelålders kvinna - NO |

Röst-ID:
- Norsk äldre man 55-60 år: `iWsqLB1KXhKYZqry79ma`.
- medelålders kvinna - NO: `wmWNq8zv8Au6slnVf0MZ`.

Båda rösterna används också i NO batch 1. Rösterna skapades med ElevenLabs eleven_v3 och `language_code: no`, en tagning per annons (flöde
"NO batch 2 – norska vinnare (Nordvask Maskinren)"). Varje fil har en .srt med samma namn och ett manus i `manus/`, där
varje norsk mening står ovanför den svenska.

## Så gjordes de

- **Manus.** Direkt översättning, 1:1 med de svenska meningarna i .srt-filen. C3:s formuleringar stramades åt med
  cirka 4 % (alla poänger och erbjudandet kvar) eftersom den svenska rösten där är mycket snabbare.
- **Röst.**
  - Hela manuset lästes i en tagning.
  - Tagningen delades på meningsgränser med espeak-DTW över hela tagningen (`espeak_cuts_hop.py`, 20 ms steg).
  - Andetagen före varje mening kortades (`trim_breaths.py`).
  - Varje mening lades nära den svenska meningens start (`plan_on_reference.py`).
  - Tempot är 1,00–1,08 med atempo, aldrig nedsaktning.
- **Pauser.** Mansrösten ger cirka 0,2 s mellan meningarna. Kvinnorösten (C4, C6, C7) är snabbare än de svenska. C4
  och C7 håller därför synken med pauser på i snitt cirka 0,8 s (högst 0,95 s). C6 har pauser på 0,6 s och slutar
  cirka 46 s, varefter bild och musik tar slutet.
- **Bild.**
  - C1, C3, C4 och C6 ligger på Vmake-textfri film (`leverans/underlag/textfri_vinnare/`).
  - C2 och C5 är byggda bildruta för bildruta ur releaserna `video11` och `video16` (`globalmap.py`,
    `b6_clean.py`), med norska CTA-kort från Nordvask-produktbilden: 50 % RABATT, PENGENE TILBAKE I 30 DAGER och
    BESTILL NÅ.
  - C7 är den svenska leveransen med svensk text borttagen med LaMa. Titeln och KJØP 2 / FÅ 2 GRATIS är omgjorda på
    norska på samma plats.
- **Skyltar och kort.**
  - C3: FØR/ETTER och Nordvask-produktkortet.
  - C4: norskt slutkort i den svenska layouten ("SALG / 4 PAKKER –50 % · FRI FRAKT / Prøv i 30 dager – pengene
    tilbake / SIKRE TILBUDET").
- **Musik.**
  - Samma spår som de svenska annonserna, i samma röst/musik-förhållande och med ljudnivån anpassad till den svenska
    annonsen (cirka −15 LUFS).
  - Musiken till video39 finns i ElevenLabs-flödet "Norrtvätt video 39 – svensk voiceover", noden "Video 39 – musikbädd".
- **Texter.**
  - 1–3 ord i Montserrat ExtraBold på de svenska annonsernas höjd.
  - Siffror skrivs med siffror: 30 dager, 19 år, 1 000, 6 000, 200 kunder, 15 000 kunder, 50 %, 999 kroner.

Verktygen finns i `leverans/underlag/norge_batch2/`.

## Att tänka på

- Några annonser visar andra märkens förpackningar på samma ställen som de svenska vinnarna, eftersom bilden är densamma:
  - Uproot i C3 och C6.
  - Tide och OxiClean i C4 och C7.
