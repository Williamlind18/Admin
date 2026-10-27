# Norska versioner: annonser från sessionen "inspiring-feynman"

Sessionen: https://claude.ai/code/session_01YTjhMMtce8VYyMS9aqb9JF (branch `claude/inspiring-feynman-uo7z24`).

När användaren i den här sessionen skriver **"gör alla annonser på norska"** gäller det **endast**
annonsen nedan. Listan är **låst 2026-10-27**. Den enda annonsen som skapades i sessionen fram till
dess är den här.

Följande ska **inte** göras på norska av det kommandot, om inte användaren nämner dem:
- svenska annonser som görs senare i den här sessionen,
- äldre annonser från andra sessioner, till exempel `norrtvatt_maskinrent_sv` (handdukarna och finnarna).

Andra sessioner har egna listor, till exempel `leverans/norska_underlag/README.md` på branchen
`claude/zealous-dijkstra-nzvyw0` och CLAUDE.md på `claude/funny-rubin-truuco`.

| Annons | Svensk leverans (den här branchen) | Svenskt manus | Källvideo | Längd |
|---|---|---|---|---|
| Maskinrent: reparatören med 19 år, biofilm och enzymer ("Det bor något i din tvättmaskin just nu.") | `leverans/norrtvatt_maskinrent_video2_sv.mp4` + `.srt` | `leverans/manus_norrtvatt_video2.txt` (73 meningar) | GitHub-release `video2`, filen `maskinrent.claude.2.mp4` (1080x1908, 30 fps) | 4:49.5 |

Obs: `norrtvatt_maskinrent2_sv` på `main` är en annan annons från en annan session ("tre lager").
Den ingår inte här.

## Så gjordes den svenska versionen (återanvänd för den norska)
- Röst: ElevenLabs `eleven_v4`, röst-ID `rvkyA7fVC0tIPFdQWCLS` ("Äldre man 1"), `language_code: "sv"`.
- Rösten lästes in i 9 sammanhängande tagningar som delades upp i meningar med `split_takes.py`, följt av
  `tighten_pauses.py`. Tagningarna var meningarna 1–9, 10–16, 17–25, 26–33, 34–41, 42–51, 52–57, 58–66
  och 67–73.
- Tidslinje: `plan_timeline.py --gap 0.2 --max-gap 0.35 --min-tempo 0.95` med de här synkpunkterna
  (meningsnummer: start i sekunder), som visar var bilderna sitter i källvideon:
  `26:98.3-98.9` ättikflaskan, `27:103.2-104.0` bikarbonatpaketet, `28:108.5-110.2` toppmataren,
  `30:117.2-119.2` butikshyllan, `34:134.1-135.2` handen som kliar, `36:142.0-143.2` hunden i fåtöljen,
  `42:163.5-165.0` petriskålen, `44:172.6-175.0` labbet/NASA, `47:184.4-185.8` sjukhuset,
  `52:204.8-206.0` alfa-amylas, `53:210.5-212.3` proteas/hårstrået, `54:217.3-219.2` lipas/fettet,
  `55:222.5-224.5` sammanfattningen, `56:225.8-228.0` kunden, `58:232.8-235.0` kvinnan med handduken,
  `60:239.0-241.2` panelen, `62:245.6-246.8` tabletten, `64:252.3-253.5` dottern och hunden,
  `65:255.8-257.0` flickan under filten, `67:260.6-262.5` produkten.
- Captions: 1–3 ord, Montserrat ExtraBold, y = 0,75. Ingen musik, eftersom originalmusiken inte gick att separera.
- TTS-stavning: "NASA:s" lästes som "Nasas" och "grand danois" som "grand danoa". Captions har rätt stavning.

## Så görs den norska versionen
- Det ska vara **samma annons**: samma klipp, samma innehåll, samma ordning och samma erbjudande, bara på
  norska (bokmål). Översätt det svenska slutmanuset naturligt och flytande, mening för mening, så att
  synkpunkterna ovan stämmer.
- Fråga användaren innan start:
  - **norskt röst-ID**,
  - om **priser, rabatt, frakt och garanti** är desamma i Norge (det svenska manuset säger "från tjugo kronor per tablett", "upp till femtio procent", "fri frakt", "trettio dagars pengarna-tillbaka-garanti", "över femton tusen kunder"),
  - om **"från svenska Norrtvätt"** ska stå kvar.
- Följ standarden i CLAUDE.md: `eleven_v4` med `language_code: "no"`, tagningar per stycke, inget
  snabbare än ×1,08, pauser på 0,2–0,3 s och Voice Isolator erbjuds mot eko.
- Uppföljning som fortfarande är öppen från den svenska versionen: Uproot Cleans förpackningar syns från
  cirka 4:10. Användaren har inte svarat på om produktbilden ska läggas över dem.
- Döp leveranserna till `norrtvatt_maskinrent_video2_no.mp4/.srt` och `manus_norrtvatt_video2_no.txt`.
