# Annonser som ska göras på norska

Låst lista, skapad 2026-10-27. När användaren skriver "gör alla annonser på norska" gäller det
**endast** annonserna nedan. Annonser som skapas efter det datumet ska inte göras på norska, om inte
användaren ber om det för just dem eller ber att de läggs till här.

Regel: samma annons, bara på norska. Samma bild, samma innehåll i samma ordning och samma synk mot
bilden. Ändra inte erbjudande eller påståenden på eget initiativ.

## 1. Norrtvätt Maskinrent, UGC-video (1:50)
- Färdig svensk version: `leverans/norrtvatt_maskinrent_sv_v2.mp4` + `norrtvatt_maskinrent_sv_v2.srt`.
  (`norrtvatt_maskinrent_sv.mp4` är samma annons med den äldre rösten.)
- Källvideo utan ny röst: GitHub-release `video1`, filen `Maskinrent.claude.mp4` (1080×1908, 110,4 s).
- Svenskt manus, 25 meningar i talad ordning: `leverans/manus_norrtvatt.txt`.
- Synkpunkter i den svenska versionen som den norska också ska träffa:
  - "det här" (Det gick så långt att jag fick det här) slutar på ögongnidningen, ca 44,3–46,6 s.
  - "orbital cellulit" ligger på det svullna ögat.
  - "Så här såg mina handdukar ut i mikroskop innan" börjar på mikroskopbilden, ca 87,4–90,0 s.
  - "Och så här ser de ut nu, efter Maskinrent" börjar på de rena fibrerna, ca 91,6–93,6 s.
- Röst: ElevenLabs `eleven_v3`. Fråga efter röst-ID för den norska rösten. Läs in i sammanhängande
  tagningar som i v2 (jämn röst), korta pauser på ca 0,2 s.
- Captions 1–3 ord i Montserrat ExtraBold, plus en norsk .srt.

## Ingår inte
- Uproot-testet, den första videon i sessionen (direktöversättning av Uproots egen annons med deras
  varumärke). Görs bara om användaren uttryckligen ber om just den.
- Landningssidorna i Shopify (de är inte annonser).
- Videor i GitHub-releaserna som inte gjordes i den här sessionen (t.ex. Norrtvatt trimmad C1–C9 och
  Slingshot).
