# Annonser som ska göras på norska

När användaren skriver **"gör alla annonser på norska"** gäller det ENDAST annonserna i listan nedan.
Annonser som skapas senare (på svenska) ska inte översättas, om de inte läggs till här uttryckligen.
Norska versioner ska vara samma annonser (samma video, upplägg, timing, musik och captions-stil), bara
på norska.

Listan låstes 2026-10-27, i sessionen där "tre misstag"-videon gjordes. Den 2026-11-02 bekräftade
användaren ("kör dom med") att även de två äldre Maskinrent-videorna (nr 2 och 3 nedan), som gjordes
före "tre misstag", hör till listan.

Norska regler (2026-11-02): varumärket heter NORDVASK och produkten MASKINREN, samma erbjudanden i
norska kronor, samma videomaterial, och rösten har samma kön som i den svenska versionen.

## 1. Norrtvätt Maskinrent – "tre misstag" (reparatören Danny)
- Svensk leverans: `leverans/norrtvatt_tre_misstag_sv.mp4`, `norrtvatt_tre_misstag_sv.srt`,
  `manus_tre_misstag.txt` (38 meningar, godkänt manus).
- Källvideo: GitHub-release `video4`, filen `Norrtvatt.claude.-.1.2.mp4` (1080x1368, 139,62 s).
- Musik: ElevenLabs-flödet `1eLBakgNB7Ol1omfnVRZ`, generationen `nEEYwopkCATWaPPoIRqJ`
  (eleven_music_v2_5, 140 s instrumental). Återanvänd samma musikbädd, `--bed-db -16`.
- Ankare (meningsnummer i det svenska manuset, starttid i s): 3 Danny 5,8-6,6 · 6 misstag ett
  17,2-18,3 · 7 bakom trumman 19,6-20,3 · 11 misstag två 33,3-33,9 · 16 misstag tre 50,3-51,2 ·
  23 NASA 74,2-75,5 · 26 alfa-amylas 85,8-87,0 · 27 proteas 90,8-92,0 · 28 lipas 96,5-97,6 ·
  29 tabletten 102,4-103,6 · 32 "Den heter Maskinrent" 114,2-115,6. Planera med `balance_plan.py`.
- **Norsk version levererad 2026-11-02:** `leverans/nordvask_tre_feil_no.mp4`, `nordvask_tre_feil_no.srt`,
  `manus_tre_feil_no.txt`. Varumärke Nordvask, produkt Maskinren, samma erbjudande i norska kronor
  (tjue kroner per tablett). Röst "Norsk äldre man 55-60 år" (`iWsqLB1KXhKYZqry79ma`), samma
  videomaterial och musikbädd, ElevenLabs-flödet `vExp6yJXq07u91Wz5e5g`.

## 2. Norrtvätt Maskinrent – video 1 ("handdukar och finnar", kvinnlig röst)
- Svensk leverans: `leverans/norrtvatt_maskinrent_sv.mp4`, `norrtvatt_maskinrent_sv.srt`,
  `manus_norrtvatt.txt` (25 meningar).
- Källvideo: GitHub-release `video1`, filen `Maskinrent.claude.mp4` (1080x1908, 110,43 s). Ingen musik.
- **Norsk version levererad 2026-11-02:** `leverans/nordvask_maskinren_no.mp4`, `nordvask_maskinren_no.srt`,
  `manus_maskinren_no.txt`. Röst "medelålders kvinna - NO" (`wmWNq8zv8Au6slnVf0MZ`), tagningen med
  `[slowly]` först (rösten var annars ~20 % snabbare än den svenska), ElevenLabs-flödet
  `rwh0wBbNLpjAcxg2OIoy`. "Tidig höstrea" blev "Akkurat nå er det salg".
- Ankare (norska meningsnummer, start i s): 10 orbital cellulitt 44,5-45,4 · 14 tabletten 56,9-57,8 ·
  21 mikroskop före 89,1-89,9 · 22 mikroskop efter 92,3-93,0. `balance_plan.py --min-tempo 0.93
  --target-gap 0.4 --max-gap 0.6`.

## 3. Norrtvätt Maskinrent – video 2 ("tre lager", kvinnlig röst)
- Svensk leverans: `leverans/norrtvatt_maskinrent2_sv.mp4`, `norrtvatt_maskinrent2_sv.srt`,
  `manus_maskinrent2.txt` (39 meningar).
- Källvideo: GitHub-release `maskinrent2`, filen `maskinrent.claude.3.mp4` (1080x1908, 135,00 s). Ingen musik.
- Etikettrutor: tre vita rutor med svart text FILM / PROTEIN / FETT (samma ord på norska) över de
  engelska etiketterna, 28,07-33,65 s (fade in 0,1 s), x 226-904, y 546-710 / 786-950 / 1021-1185,
  Montserrat ExtraBold fs 91, fsp 3,5, textfärg &H141414.
- **Norsk version levererad 2026-11-02:** `leverans/nordvask_maskinren2_no.mp4`, `nordvask_maskinren2_no.srt`,
  `manus_maskinren2_no.txt`. Röst "medelålders kvinna - NO" (`wmWNq8zv8Au6slnVf0MZ`), ElevenLabs-flödet
  `VmMgTkz5ysn7L1PYT5pR`. "Höstrea" blev "Akkurat nå er det salg".
- Ankare (start i s): 5 eddik 9,2-9,9 · 11 tre lag 26,5-27,3 · 14 steg to 38,3-39,0 · 23 steg tre
  65,0-65,8 · 24 én tablett 67,1-67,9 · 26 alfa-amylase 78,0-78,8 · 27 protease 83,3-84,1 · 28 lipase
  89,2-90,0 · 34 én tablett med alle tre 108,6-109,3 · 39 bestill 130,7-131,5.
