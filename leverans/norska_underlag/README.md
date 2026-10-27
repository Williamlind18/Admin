# Norska versioner: vilka annonser som ingår

När användaren skriver **"gör alla annonser på norska"** gäller det **endast** de sex annonserna nedan.
De skapades i sessionen https://claude.ai/code/session_01QhHuFebkp7vMxHNSYjPx5q (29 sep–14 okt 2026).

Annonser som inte står här ska **inte** göras på norska av det kommandot. Det gäller både äldre annonser
(`norrtvatt_maskinrent_sv`, `norrtvatt_maskinrent2_sv`) och alla nya svenska annonser som görs senare.

| Svensk leverans | Källvideo (GitHub-release / fil) | Innehåll | Längd | Svensk röst-ID | Täckrutor |
|---|---|---|---|---|---|
| `norrtvatt_maskinrent3_sv` | `video6` / `0928.2.mp4` | NASA-enzymer, "smutsigare än din toalett" | 3:59.6 | p47LfPZdd7LXERMMfx1R | inga |
| `norrtvatt_maskinrent4_sv` | `video10` / `Norrtvatt.trimmad.-.c2.mp4` | Dotterns utslag | 4:09.4 | LzJuwbGODHbc1VvzbMrf | 3:54.90–3:56.98 "30 DAGARS PENGARNA TILLBAKA", se `maskinrent4_tackrutor.ass` |
| `norrtvatt_maskinrent5_sv` | `video12` / `norrtvatt_-_konkurrent_4.mp4` | Enzymskum | 0:56.3 | UPl4IVQHmNGPUn6Qs7Uf | 0:00.00–0:05.11 rubrikruta, se `maskinrent5_tackrutor.ass` |
| `norrtvatt_maskinrent6_sv` | `video13` / `Norrtvatt.trimmad.-.c4.mp4` | "Ren tvätt börjar i tvättmaskinen" | 0:58.7 | tY9FLUZCUCQXwZYDwvWw | inga |
| `norrtvatt_maskinrent7_sv` | `video16` / `Norrtvatt.trimmad.-.C6.mp4` | Reparatören som skulle skrota maskinen | 3:41.8 | OvO33bxTqNfwQfoR6mVh | inga |
| `norrtvatt_maskinrent8_sv` | `video18` / `Norrtvatt.trimmad.-.c8.mp4` | Ursäkten / "vi har hållit inne med något" | 1:01.7 | LzJuwbGODHbc1VvzbMrf | 4 st, se `maskinrent8_tackrutor.ass` |

Det svenska manuset till varje annons ligger i `leverans/manus_maskinrentN.txt`.

## Så görs den norska versionen
- Innehållet ska vara **samma annons**: samma klipp, samma manus och samma erbjudande, bara på norska (bokmål).
  Utgå från det svenska manuset och översätt det naturligt och flytande. Använd inte engelskan.
- Följ `ad-video-localizer`-skillen som vanligt: eleven_v3, en tagning som delas upp med `split_take.py`,
  atempo ≤ ~1.08, pauser ~0.2 s, textning med 1–3 ord i Montserrat ExtraBold, ny ElevenLabs-musik,
  och leverans som förhandsvisning i chatten, mp4 på GitHub och .srt.
- Alla täckrutor ska ha samma position och tid men med norsk text, till exempel "30 DAGARS PENGARNA TILLBAKA"
  → "30 DAGERS PENGENE TILBAKE" och "REAN SLUTAR SNART" → "SALGET SLUTTER SNART".
- Källvideon till `maskinrent5` var 480x848 och skalades upp (lanczos + unsharp) till 1080x1908.
- I `maskinrent8` byttes bildrutorna 1594–1601 (53,133–53,367 s, jättestora "ENDS"-bokstäver) mot en
  stillbild av bildruta 1602.
- `maskinrent7` blev över 100 MB och kodades om i två pass (~3200k) för att få plats på GitHub.
- Fråga användaren innan start: **norskt röst-ID**, och om erbjudandet, valutan och varumärket är desamma i Norge.
- Döp leveranserna till `norrtvatt_maskinrentN_no.mp4/.srt` och `manus_maskinrentN_no.txt`.
