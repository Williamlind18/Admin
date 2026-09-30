# Slingshot jul 2026: annonser att köra

**Allt du ska köra ligger i [`ANNONSER_ATT_KORA/`](ANNONSER_ATT_KORA).** Varje undermapp är *en*
annonsgrupp i Meta. Allt i samma mapp körs tillsammans, och olika mappar blandas aldrig.

| Annonsgrupp (mapp) | Målgrupp och åldersförslag | Annonser |
|---|---|---|
| [AG1 Julklappen till barnbarnen](ANNONSER_ATT_KORA/AG1_Barnbarn__MG-A_45-65) | MG-A mor- och farföräldrar, 45–65+ | 2 videor + 1 stillbild |
| [AG2 Bordshockey-nostalgi](ANNONSER_ATT_KORA/AG2_Bordshockey-nostalgi__MG-A_45-65) | MG-A mor- och farföräldrar, 45–65+ | 2 videor + 1 stillbild |
| [AG3 Skärmfritt](ANNONSER_ATT_KORA/AG3_Skarmfritt__MG-B_30-50) | MG-B föräldrar, 30–50 | 2 videor |
| [AG4 3 skäl](ANNONSER_ATT_KORA/AG4_Tre-skal__MG-B_30-50) | MG-B föräldrar, 30–50 | 2 videor |
| [AG5 Julafton](ANNONSER_ATT_KORA/AG5_Julafton__MG-C_25-65) | MG-C hela familjen, 25–65+ (bred) | 2 videor + 1 stillbild |
| [AG6 Sista pucken](ANNONSER_ATT_KORA/AG6_Sista-pucken__MG-C_25-65) | MG-C hela familjen, 25–65+ (bred) | 2 videor |

När du öppnar en mapp visas en tabell med annonsnamn och AI-märkning, följd av texterna att klistra in
(primärtexter, rubrik, beskrivning och CTA).

**Ladda ner:** öppna filen på GitHub och klicka på nedladdningsknappen (pilen uppe till höger).

---

## Så här sätter du upp det

| Fas | Kampanj | Upplägg |
|---|---|---|
| 1. Test (okt–mitten av nov) | `SS \| Jul26 \| Sales \| TEST \| ABO` | Alla 6 annonsgrupper, med lika budget (förslag 400–500 kr/dag var). Utvärdera efter 4–7 dagar, eller när varje grupp har spenderat minst 2× CPA (ca 500 kr). |
| 2. Skala (mitten av nov–6 dec) | `SS \| Jul26 \| Sales \| SCALE \| CBO` | Flytta de 2–3 vinnande annonsgrupperna hit. Använd samma post-ID, så att kommentarer och likes följer med. Höj kampanjbudgeten med 20–30 % per steg. |

- **Gemensamma inställningar:** Sverige, mål Försäljning/Köp, Advantage+ placeringar, 7 dagars klick och
  1 dags visning, samt Advantage+ målgrupp med åldersförslaget ovan.
- **Sista beställningsdag för julleverans:** söndag 6 december. Stäng julbudskapet efter det, eller sänk
  budgeten kraftigt.
- **Inlärning:** Meta vill ha cirka 50 köp per vecka och annonsgrupp. Med fjolårets cirka 240 kr per köp
  motsvarar det cirka 1 700 kr/dag per grupp. "Begränsad inlärning" är därför ok i testfasen. I
  skalfasen ska vinnarna ligga i CBO med tillräcklig budget.
- **Namngivning:** annonsgruppen heter t.ex. `MG-A | AG1 Barnbarn | 45-65+ | Adv+` och annonsen
  `AG1-A1 | Text | Montage | 19s`. Exakta namn står i varje mapp.

## Bra att veta om materialet
- **Textvideorna A1, B1, C1, E1, F1 och F2 är 100 % riktigt spelmaterial.** Den inbrända hösttexten
  är borttagen.
- **Markera som AI-innehåll i Meta:** AG1-A2, AG2-B2, AG3-C2, AG4-D1, AG4-D2, AG5-E2 och alla
  stillbilder. De innehåller AI-klipp (paketöppning och julgran) eller AI-bilder, och Meta visar en
  "AI info"-etikett i EU.
- **Voiceover-videorna:** ElevenLabs v3. Kvinnlig röst i A2 och C2, manlig röst i B2, D2 och E2. Hela
  manuset är läst i en tagning, spelljudet ligger lågt under rösten och ljudnivån är normaliserad till
  -14 LUFS.
- **Text i bild ligger i övre halvan av brädet.** Där täcker den inga händer eller skott, och den ligger
  inom Reels säkra yta och inom 4:5-beskärningen.
- **Undertexterna är inbrända.** Ladda därför *inte* upp några `.srt`-filer i Meta, eftersom det kan ge
  dubbel text. `.srt`-filerna och manusen ligger i [`extra_srt-och-manus/`](extra_srt-och-manus), för
  TikTok/YouTube eller om du vill göra om något.
