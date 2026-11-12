# Ny batch 6 – upplägg i Meta (Maskinrent, Norrtvätt)

Den här mappen innehåller allt som behövs för att lägga upp **ny batch 6** i Meta: 15 videoannonser (5 koncept × 3 hooks),
undertexter, manus och exakt hur annonsgrupperna ska byggas. Batch 6 är vanliga iterationer, **inte** Black Friday
(BF-annonserna ligger i `leverans/blackfriday/` och körs i en egen BF-kampanj).

Repo: `williamlind18/Admin`, branch `claude/funny-rubin-truuco`, mapp `leverans/batch6_meta/`.

---

## Till en ny Claude-session (klistra in som första meddelande)

> Läs `leverans/batch6_meta/README.md` i repot williamlind18/Admin (branch claude/funny-rubin-truuco) och hjälp mig
> lägga upp ny batch 6 i Meta enligt den. Svara på svenska. Ändra inget i befintliga kampanjer, annonsgrupper eller
> budgetar och publicera inget utan att fråga mig först.

---

## Läget i kontot (senaste 7 dagarna, avläst 12 november 2026)

- Kampanjen **"CBO - Maskinrent"**: 6 960 kr/dag, budgetstrategi högsta volym, 46 100 kr spend, ROAS 5,8.
- Varje batch ligger som en egen annonsgrupp med **minsta spend 170 kr/dag**.

| Annonsgrupp | Spend 7 d | ROAS |
|---|---|---|
| ny batch 4 | 31 800 kr | 5,7 |
| ny batch 5 | 7 400 kr | 6,1 |
| ny batch 5.1 | 4 000 kr | 6,3 |
| ny batch 4.1 | 1 200 kr | 4,7 |
| ny batch 3.1 - LP | 1 200 kr | 6,1 |

Batch 5 och 5.1 fick budget trots att batch 4 dominerar, så upplägget med en annonsgrupp per batch och minsta spend
i samma CBO fungerar. Därför läggs batch 6 i samma kampanj, inte i en egen test-CBO. Det ersätter rådet i
`batchplan_b6.md`. En vinnare kan då skala direkt, utan att flyttas och börja om i inlärningen.

---

## Upplägget

**Kampanj:** befintliga "CBO - Maskinrent". Skapa ingen ny kampanj.

**Annonsgrupper:** fem nya, en per koncept, med tre annonser (H1–H3) i varje.
- Enklast är att **duplicera annonsgruppen "ny batch 5"**, så får de nya samma målgrupp, placeringar och optimering.
  Ta sedan bort de kopierade annonserna och byt namn.
- Minsta spend: **170 kr/dag** per annonsgrupp, som för de andra batcherna.

**Budget:** de fem golven tar 850 kr/dag. Höj CBO-budgeten med ungefär lika mycket under testveckan, till cirka
7 800 kr/dag, så att batch 4 inte trycks ned.

**Rör inte** ny batch 4. Den bär kontot.

**Varför en grupp per koncept och inte en grupp med 15 annonser:** i en enda grupp lägger Meta nästan allt på 1–2
annonser, och då går det inte att se hur de andra koncepten står sig. Med en grupp per koncept får alla fem en
garanterad chans. Inom gruppen väljer Meta hook, och hur spenden fördelas mellan hookarna blir i sig ett resultat.

**Annonstext och länk:** samma primärtext, rubrik och produktsida som i batch 5-annonserna. Det här är iterationer,
så bara videon byts. Landningssida: den vanliga produktsidan.

**Undertexter:** texten är redan inbränd i videorna. Ladda **inte** upp .srt-filerna i Meta, då blir det dubbel text,
och slå av automatisk textning. .srt-filerna är bara referens.

**Format:** alla videor är 9:16 utom C3, som är 4:5 (samma som sin förälder b3.1 C8).

---

## Annonsgrupper och annonser

Namn i Ads Manager, enligt Spencers metod:

`ny batch 6 – C2 | I2-b4C2 | vinkel | auktoritet | medvetenhet | format`

- **`ny batch 6 – C2`** är konceptets unika nummer, Spencers "Batch#". Det återanvänds aldrig.
- **`I2-b4C2`** pekar på föräldern: iteration 2 av b4 C2. Söker du på "b4C2" i Ads Manager ser du alla iterationer av
  vinnaren och hur de gick.
- **Vinkel, auktoritet, medvetenhet och format** visar vad som skiljer konceptet från andra, så att du kan filtrera
  på en komponent när du märker vinnare.
- **Annonserna** får samma början plus hooknummer och vilken komponent hooken leder med, till exempel
  `ny batch 6 – C2 H1 | I2-b4C2 | omedveten`.

| Annonsgrupp | Annonser |
|---|---|
| `ny batch 6 – C1 \| I1-b4C2 \| lukten bakom panelen \| ägaren + teknikern \| lösningsmedveten \| berättelse` | `ny batch 6 – C1 H1 \| I1-b4C2 \| lösningsmedveten` · `… C1 H2 \| I1-b4C2 \| auktoritet` · `… C1 H3 \| I1-b4C2 \| status` |
| `ny batch 6 – C2 \| I2-b4C2 \| lukten bakom panelen \| teknikern + isärplockning \| omedveten \| berättelse` | `ny batch 6 – C2 H1 \| I2-b4C2 \| omedveten` · `… C2 H2 \| I2-b4C2 \| intensitet` · `… C2 H3 \| I2-b4C2 \| auktoritet` |
| `ny batch 6 – C3 \| I1-b3.1C8 \| slipp köpa ny maskin \| teknikern + före/efter \| problemmedveten \| berättelse 4:5` | `ny batch 6 – C3 H1 \| I1-b3.1C8 \| pengar` · `… C3 H2 \| I1-b3.1C8 \| resultatet först` · `… C3 H3 \| I1-b3.1C8 \| auktoritet + pengar` |
| `ny batch 6 – C4 \| I1-b3C3 \| mögel i gummilisten \| reparatören + gummilisten \| problemmedveten \| berättelse` | `ny batch 6 – C4 H1 \| I1-b3C3 \| lösningsmedveten` · `… C4 H2 \| I1-b3C3 \| status` · `… C4 H3 \| I1-b3C3 \| auktoritet + brådska` |
| `ny batch 6 – C5 \| I1-b1C3 \| det bor något i maskinen \| reparatören + panelen av \| omedveten \| berättelse` | `ny batch 6 – C5 H1 \| I1-b1C3 \| ärvd hook` · `… C5 H2 \| I1-b1C3 \| auktoritet + bevis` · `… C5 H3 \| I1-b1C3 \| husdjur` |

I tabellen ovan står `…` för `ny batch 6 –`.

### C1 – ägaren berättar (`ny batch 6 – C1 | I1-b4C2 | …`)
Mapp `C1_I1-b4C2_agaren/`. Förälder b4 C2 (genombrott). Ändrat: ägaren berättar i stället för teknikern. Auktoritet:
teknikern (i tredje person) och isärplockningen i bild.

| Annons | Hook | Fil |
|---|---|---|
| H1 (ärvd, lösningsmedveten) | "Jag körde maskinrengöring i tvättmaskinen varje månad. Ändå luktade allt jag tvättade hund." | [norrtvatt_maskinrent11_agaren_h1_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C1_I1-b4C2_agaren/norrtvatt_maskinrent11_agaren_h1_sv.mp4) |
| H2 (auktoritet) | "En tekniker öppnade min tvättmaskin och sa åt mig att slänga allt rengöringsmedel jag köpt." | [norrtvatt_maskinrent11_agaren_h2_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C1_I1-b4C2_agaren/norrtvatt_maskinrent11_agaren_h2_sv.mp4) |
| H3 (status) | "Jag slutade bjuda hem folk, för handdukarna luktade hund. Och jag rengjorde ändå maskinen varje månad." | [norrtvatt_maskinrent11_agaren_h3_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C1_I1-b4C2_agaren/norrtvatt_maskinrent11_agaren_h3_sv.mp4) |

### C2 – "Visste du att…" (`ny batch 6 – C2 | I2-b4C2 | …`)
Mapp `C2_I2-b4C2_visste-du/`. Förälder b4 C2. Ändrat: medvetenheten sänks till omedveten, och första raden får
högre intensitet. Auktoritet: teknikern och isärplockningen i bild.

| Annons | Hook | Fil |
|---|---|---|
| H1 (omedveten) | "Visste du att det finns ett utrymme i din tvättmaskin som aldrig blir rent? …" | [nb6_C2_H1_I2-b4C2_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C2_I2-b4C2_visste-du/nb6_C2_H1_I2-b4C2_sv.mp4) |
| H2 (intensitet) | "Bakom trumman i din tvättmaskin lever det något just nu. …" | [nb6_C2_H2_I2-b4C2_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C2_I2-b4C2_visste-du/nb6_C2_H2_I2-b4C2_sv.mp4) |
| H3 (auktoritet) | "Efter nitton år som reparatör vet jag var lukten i tvätten kommer ifrån. …" | [nb6_C2_H3_I2-b4C2_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C2_I2-b4C2_visste-du/nb6_C2_H3_I2-b4C2_sv.mp4) |

### C3 – före/efter, pengar, 4:5 (`ny batch 6 – C3 | I1-b3.1C8 | …`)
Mapp `C3_I1-b3.1C8_fore-efter/`. Förälder b3.1 C8 (genombrott). Ändrat: drivkraften blir pengar, och resultatet
visas först. Auktoritet: teknikern och före/efter i bild.

| Annons | Hook | Fil |
|---|---|---|
| H1 (pengar) | "Innan du köper en ny tvättmaskin för tusentals kronor, titta bakom panelen på den gamla." | [nb6_C3_H1_I1-b3.1C8_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C3_I1-b3.1C8_fore-efter/nb6_C3_H1_I1-b3.1C8_sv.mp4) |
| H2 (resultatet först) | "Samma tvättmaskin, före och efter en enda tablett. …" | [nb6_C3_H2_I1-b3.1C8_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C3_I1-b3.1C8_fore-efter/nb6_C3_H2_I1-b3.1C8_sv.mp4) |
| H3 (auktoritet och pengar) | "En kund bad mig skrota sin tre år gamla tvättmaskin. Det enda som var fel satt bakom panelen." | [nb6_C3_H3_I1-b3.1C8_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C3_I1-b3.1C8_fore-efter/nb6_C3_H3_I1-b3.1C8_sv.mp4) |

### C4 – reparatören och gummilisten (`ny batch 6 – C4 | I1-b3C3 | …`)
Mapp `C4_I1-b3C3_gummilisten/`. Förälder b3 C3 (genombrott, på gränsen till KPI-målet). Ändrat: tre nya hooks,
där H1 bär C2:s lärdom, och en stramare mitt. Auktoritet: reparatören, som drar undan gummilisten i bild.

| Annons | Hook | Fil |
|---|---|---|
| H1 (lösningsmedveten) | "Kör du maskinrengöring varje månad och luktar tvätten ändå hund? …" | [nb6_C4_H1_I1-b3C3_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C4_I1-b3C3_gummilisten/nb6_C4_H1_I1-b3C3_sv.mp4) |
| H2 (status) | "Hon visste aldrig om kollegorna kände lukten när hon satt bredvid dem. …" | [nb6_C4_H2_I1-b3C3_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C4_I1-b3C3_gummilisten/nb6_C4_H2_I1-b3C3_sv.mp4) |
| H3 (auktoritet och brådska) | "Efter nitton år som reparatör säger jag samma sak i varje hem med hund: du långkokar kläderna i mögel." | [nb6_C4_H3_I1-b3C3_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C4_I1-b3C3_gummilisten/nb6_C4_H3_I1-b3C3_sv.mp4) |

### C5 – beviset i bild (`ny batch 6 – C5 | I1-b1C3 | …`)
Mapp `C5_I1-b1C3_beviset/`. Förälder b1 C3 (spendvinnare: Meta gillar den, men den säljer dyrt). Ändrat:
- Panelen skruvas av och beviset visas redan efter cirka 25 s.
- Mekanismen är stramare.
- Annonsen är kortare, cirka 3 min.

| Annons | Hook | Fil |
|---|---|---|
| H1 (ärvd) | "Det bor något i din tvättmaskin just nu. …" | [nb6_C5_H1_I1-b1C3_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C5_I1-b1C3_beviset/nb6_C5_H1_I1-b1C3_sv.mp4) |
| H2 (auktoritet med bevis) | "Jag skruvade av panelen på en tvättmaskin i ett hem med hund. Det här bodde bakom trumman." | [nb6_C5_H2_I1-b1C3_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C5_I1-b1C3_beviset/nb6_C5_H2_I1-b1C3_sv.mp4) |
| H3 (husdjur, omedveten) | "Har du husdjur? Då ser det troligen ut så här bakom trumman i din tvättmaskin." | [nb6_C5_H3_I1-b1C3_sv.mp4](https://github.com/williamlind18/Admin/raw/claude/funny-rubin-truuco/leverans/batch6_meta/C5_I1-b1C3_beviset/nb6_C5_H3_I1-b1C3_sv.mp4) |

---

## Tidplan och utvärdering

- **Lansera nu,** så får testet en hel vecka innan Black Friday-trycket tar i.
- **Märk resultaten den 19–20 november,** efter 7 dagar.
- **Jämför relativt:** när BF-kampanjen startar blir annonsutrymmet dyrare. Jämför därför batch 6 med batch 4 och 5
  under samma dagar, inte med siffror från före.

**Så läser du resultatet (Spencer):**

| Ruta | Kännetecken | Drag |
|---|---|---|
| Genombrott | Tar en stor del av kampanjens spend (minst cirka 30 % för ett konto i den här storleken) och ROAS kring 5,8 eller bättre | Låt gå, ta bort golvet, gör nästa batch på konceptet |
| KPI-vinnare | Bra ROAS men tar bara sina 170 kr/dag | Ta bort golvet och se om det klarar sig på egen hand, testa nya hooks eller format |
| Spendvinnare | Tar budget men låg ROAS | Behåll hook och format, stärk auktoritet, mekanism och positionering |
| Förlorare | Varken spend eller ROAS | Pausa annonsgruppen |

Inom en annonsgrupp visar spendfördelningen mellan H1, H2 och H3 vilken hook Meta tror på. Ta med den in i nästa batch.

---

## Filer i mappen
- `C1_…/` till `C5_…/`: tre videor (.mp4, full kvalitet), tre undertextfiler (.srt) och manuset för konceptet.
- `batchplan_b6.md`: den ursprungliga batchplanen med lärdomarna bakom varje koncept. Där står att batch 6 ska ha
  en egen test-CBO, men den rekommendationen ersätts av upplägget ovan.
- Röst i alla 15: ElevenLabs, "Äldre man 50-60 år - SE".
