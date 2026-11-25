# DK batch 2: danska versioner av NO batch 2 (Nordvask Maskinren)

Samma sju annonser som NO batch 2 (`leverans/norge_batch2/`), på danska. Samma bild, musik, texthöjd och erbjudande som de
svenska annonserna, med Nordvask Maskinren, DKK och shopnordvask.dk.

C1, C3, C4 och C6 fanns redan på danska sedan 2026-11-20 (`leverans/danmark/`) och är samma filer här. C2, C5 och C7 är
nya (2026-11-25).

| DK batch 2 | Svensk annons (Meta) | Svensk leverans (sökväg @ gren) | Danska filen kommer från | Längd | Röst |
|---|---|---|---|---|---|
| `Nordvask DK batch 2 - C1.mp4` | b4 C2 | `leverans/norrtvatt_video22_sv.mp4` @ `claude/quirky-mayer-tsglxb` | `leverans/danmark/nordvask_dk_b4-C2_da.mp4` | 3:48 | dansk man 40–50 år |
| `Nordvask DK batch 2 - C2.mp4` | b6 C4 H1 (iteration av b3 C3) | `leverans/batch6/nb6_C4_H1_I1-b3C3_sv.mp4` @ `claude/funny-rubin-truuco` | ny | 3:06 | dansk man 40–50 år |
| `Nordvask DK batch 2 - C3.mp4` | b5 C2 | `leverans/norrtvatt_vsl_reparator.mp4` @ `claude/video-editing-15noqg` | `leverans/danmark/nordvask_dk_b5-C2_da.mp4` | 3:30 | dansk man 40–50 år |
| `Nordvask DK batch 2 - C4.mp4` | b5.1 C3 | `leverans/norrtvatt_video43_tre_enzymer_sv.mp4` @ `claude/focused-hamilton-930j6d` | `leverans/danmark/nordvask_dk_b5.1-C3_da.mp4` | 3:51 | dansk kvinna 30–40 år |
| `Nordvask DK batch 2 - C5.mp4` | b6 C3 H3 (iteration av b3.1 C8) | `leverans/batch6/nb6_C3_H3_I1-b3.1C8_sv.mp4` @ `claude/funny-rubin-truuco` | ny | 3:09 | dansk man 40–50 år |
| `Nordvask DK batch 2 - C6.mp4` | b5 C5 | `leverans/norrtvatt_maskinrent9_enzymer_sv.mp4` @ `claude/funny-rubin-truuco` | `leverans/danmark/nordvask_dk_b5-C5_da.mp4` | 0:53 | dansk kvinna 40–50 år |
| `Nordvask DK batch 2 - C7.mp4` | b5 C6 (video39) | `leverans/norrtvatt_video39_sv.mp4` @ `claude/quirky-mayer-tsglxb` | ny | 1:49 | dansk kvinna 40–50 år |

Röst-ID: dansk man 40–50 år `Fc1E2eP0cRA7NC70Jdgt`, dansk kvinna 40–50 år `B1bvPObPV34zuzdnfbgb`, dansk kvinna 30–40 år
`V0yHo4Uc035mmE6kOCLc`.

Varje video har en .srt med samma namn och ett manus i `manus/`, där varje dansk mening står ovanför den svenska.

## Så gjordes C2, C5 och C7

- **Manus.** Direkt översättning från svenskan, 1:1 med meningarna i den svenska .srt-filen, med norskan som stöd. Ordvalen
  följer de danska b3 C3 och b3.1 C8 (C2 och C5 är iterationer av dem).
- **Röst.** ElevenLabs `eleven_v4`, språkkod `da`, en tagning per stycke om 5–6 meningar (flödet "DK batch 2 – danska
  versioner av NO batch 2 C2, C5, C7 (Nordvask Maskinren)"). Tagningarna delades i meningar med espeak-DTW och snitt i
  riktiga pauser, och varje dansk mening börjar där den svenska började (högst 0,22 s ifrån). Tempo 0,92–1,075 med atempo,
  pauser 0,2–0,87 s.
- **Bild.**
  - C2 och C5 är byggda bildruta för bildruta ur releaserna `video11` och `video16`, klippta exakt som de svenska
    (`globalmap.py`, `b6_clean.py`). Danska kort från Nordvask-produktbilden: 50 % RABAT, PENGENE TILBAGE I 30 DAGE och
    BESTIL NU (`cards_da.py`).
  - C7 är den svenska leveransen med den svenska texten borttagen med LaMa. Titeln ("Én enzymtablet. / Det her kom ud af
    en / "ren" vaskemaskine.") och erbjudandet (KØB 2 / FÅ 2 GRATIS / Fri fragt + 30 dages pengene-tilbage-garanti) är
    omgjorda på danska på samma plats, i samma typsnitt och storlek och med samma in- och uttoning (`c7_overlays_da.py`).
- **Musik.** Samma musik som de svenska annonserna, på samma ställe och i samma röst/musik-förhållande, med ljudnivån
  matchad mot den svenska (cirka −15 LUFS). C2 och C5: `music120` med loopen vid 107,5 s som i batch 6. C7: "Video 39 –
  musikbädd" ur ElevenLabs-flödet "Norrtvätt video 39 – svensk voiceover".
- **Texter.** 1–3 ord i Montserrat ExtraBold, på de svenska annonsernas höjd (C2 och C5 75 %, C7 71 %; i C7 ligger texten
  på 36 % mellan 55,6 och 58,2 s, som i den svenska). Belopp och större tal som siffror: 50 %, 30 dage, 19 år, 1.000.

Verktygen finns i `leverans/underlag/danmark_batch2/`.
