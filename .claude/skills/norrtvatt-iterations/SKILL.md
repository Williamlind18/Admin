---
name: norrtvatt-iterations
description: "Brand file and iteration playbook for Norrtvätt's Maskinrent enzyme tablets for washing machines (Swedish; the Norwegian version is Nordvask Maskinren) and for the Uproot Clean ads they are built on - the same Uproot ads that Spencer (Evolve) breaks down in his ad-iteration keynote. Holds the product facts and offer, claims that need checking, the catalogue of Maskinrent ads 1-10 with source tags, files and component cards, the Uproot original and its two winning iterations, and a backlog of ready iteration briefs with Swedish hooks. Use it together with ad-iterations whenever the user wants a new Maskinrent or Norrtvätt ad, an iteration, new hooks or a format swap of one of their ads, a breakdown of an Uproot Clean ad, to label which Maskinrent ads win, or to plan the next batch - e.g. 'gör en iteration på mögel-annonsen', 'nästa maskinrent-annons', 'vilka maskinrent-annonser vinner', 'gör uproot-annonsen med morfar', 'nya hooks till maskinrent'."
---

# Norrtvätt / Maskinrent iterations

This is the brand file for Norrtvätt. Use it on top of the `ad-iterations` skill, which holds the
method (label → learnings → iterate). Produce video ads with the `ad-video-localizer` skill and
follow the standing video preferences in the repo's CLAUDE.md. Answer in Swedish.

Our Maskinrent ads are imitation ads of Uproot Clean, and Uproot is the brand Spencer uses as his
worked example. His breakdown therefore applies directly. Maskinrent 6 is almost exactly his
"iteration 2", which is Uproot's top ad. Two of his proven Uproot ads have no Swedish version yet:
the grandpa original and the grandpa/status iteration. Details: `references/uproot-breakdown.md`.

## Product facts (from our scripts; recheck the shop page when unsure)
- **Product:** Maskinrent from Norrtvätt, a small Swedish company. An enzyme tablet that cleans the
  washing machine, made for homes with pets. Norwegian brand: Nordvask Maskinren.
- **Use:** one tablet, empty drum, a hot program. Then one tablet a month to keep the coating from
  coming back. Twelve tablets last a year. Fits all washing machines.
- **Mechanism:** three enzymes, each with a job:
  - *Alfa-amylas* dissolves the detergent and softener film that holds everything to the drum.
  - *Proteas* breaks down keratin, the protein in pet hair, so the hair finally rinses out.
  - *Lipas* removes the fat (sebum, "talg") that the odor bacteria live on.
  - Short form: "Ett blottar, ett förstör och ett svälter ut resten."
- **Where it works:** behind the drum (the sealed space between inner and outer drum), under the door
  seal, in the hoses and around the detergent drawer.
- **Positioning:** made for pet homes. The big brands' machine cleaners are mostly oxygen bleach, which
  can't break down protein or fat. Enzymes dissolve the coating instead of rinsing over it.
- **Current offer** (Maskinrent 4-10, last checked 2026-11-04): köp två, få två på köpet = four packs
  for 999 kr, about 250 kr per pack and about 20 kr per tablet, free shipping, 30-day money-back
  guarantee. Earlier offers (autumn sale up to 50 %, two years for 619 kr) are expired. Don't reuse
  them without asking.
- **Offer in the live "ny batch 4" ads** (B11; confirmed by the user 2026-11-04 for B12): 50 % rabatt,
  one pack (12 tablets) lasts a whole year, 30 days money back. Shop price 499 kr. Ask which offer to use
  when a new ad is made.
- **Numbers in TTS:** write them as words ("niohundranittionio kronor", "trettio dagar").

## Claims that need the user's OK before reuse
These appear in earlier scripts. Ask once whether they are still true before using them again, and
flag the story-type ones once:
- "Över femtontusen kunder", "betyget fyra komma åtta av fem".
- The enzymes "come from NASA" research.
- "Skonsam mot maskinen och utan starka kemikalier", "avkalkar".
- Persona authority: technician for 10 or 19 years with over a thousand machines taken apart; a
  laundromat owner with 22 machines. An AI voice telling an invented first-person story can count as
  misleading marketing under marknadsföringslagen. The user decides.
- Health stories (orbital cellulitis, staphylococci, "my doctor said").
- Don't name competitors (Affresh, Tide, OxiClean, Uproot). Maskinrent 7 named three; newer scripts
  don't.

## Ad catalogue
Full component cards: `references/ad-catalogue.md`. Scripts and deliveries are in `leverans/`. The
source videos are GitHub releases on this repo, named by tag.

| Batch | Ad | Source tag | Angle in one line | Authority | Awareness |
|---|---|---|---|---|---|
| B01 | Maskinrent 1, towels and acne | – | Dirty machine gives skin problems | Own story, doctor, microscope | Unaware |
| B02 | Maskinrent 2, three layers | – | Cleaners take one layer of three | Step-by-step format | Solution |
| B03 | Maskinrent 3, UV test | video8 | Clean-looking laundry is dirty | Technician + UV test | Problem |
| B04 | Maskinrent 4, biofilm | video9 | The smell is something living | Technician 19 yrs, case story | Solution |
| B05 | Maskinrent 5, three mistakes | video17 | Three mistakes pet owners make | Technician + list | Problem |
| B06 | Maskinrent 6, mold | video19 | Machine slow-cooks clothes in mold | List format | Unaware |
| B07 | Maskinrent 7, laundromat | video27 | Smell sits in the machine | Laundromat owner, 22 machines | Solution |
| B08 | Maskinrent 8, laundry tricks | video35 | Three tricks you do wrong | List format | Unaware |
| B09 | Maskinrent 9, enzymes | video41 | Three enzymes others lack | The mechanism itself | Product |
| B10 | Maskinrent 10, technician | video44 | See what came out after one wash | Technician teardown | Problem |
| B11 | C2 in "ny batch 4", monthly cleaner | video22 | Don't scrap it; shelf cleaners can't reach | Technician teardown | Solution |
| B12 | I1-B11, the owner tells it (3 hooks) | video22 | Same, told by the older male owner | Technician (3rd person) + teardown | Solution |

Norwegian versions of B03-B06 exist (`nordvask_maskinren*_no.mp4`). Name them `B03-NO` and so on.
Per CLAUDE.md, only Maskinrent 3-6 get Norwegian versions unless the user names others.

**Built-in tests once labeled.** Several pairs differ in one or two components, so their labels are
learnings by themselves:
- **B06 vs B08:** the same body, a different hook intensity (mold vs "tricks you do wrong").
- **B04 vs B07:** the same long story beats, a different authority (technician vs laundromat owner).
- **B05 vs B06:** list format with vs without a technician, a pet avatar vs a broad one.
- **B03 vs B10:** two demonstrations (UV test vs teardown).
- **B09 vs B02:** a short vs a long mechanism explainer.

## How to run a round for Norrtvätt
1. **Label.** Read the last 30 days per ad from the Meta Ads connector and the Trackpanda connector
   ("Norrtvätt sverige"). The account is in SEK, so pass `--fx` (SEK per USD, about 10-11; check the
   rate). The account is under 100k USD a month, so a breakthrough takes at least 30 % of its campaign's
   spend after 7 days (the script's default). Map
   ad names to batch numbers with the catalogue above, then add the box to `references/ad-catalogue.md`.
2. **Learnings.** Update the component cards with what the labels show, starting with the built-in
   test pairs. Date every learning.
3. **Iterate.** Pick from `references/backlog.md` or write new briefs with the `ad-iterations`
   templates. Every brief names a clear, true authority (a requirement; the technician with a teardown
   is our proven one, the Uproot grandpa is only Spencer's example). Show the user the brief and the
   script before generating any voice.
4. **Produce.** Use `ad-video-localizer`. Ask for the voice ID. Read all three hooks in the same take.
   New competitor source videos go up as the next free GitHub release tag (video48, video49…).
5. **Name.** Every new ad gets the next free batch number (B11, B12 and so on). An iteration adds a
   pointer to its parent: `B11 | I1-B06 | angle | authority | awareness | format | H1` is iteration 1
   of B06. A new Uproot source with no parent has no I part.
6. **Record.** Add the new ad to the catalogue and the learning to the dated list below.

## Landing pages
Keep the evergreen product page for all ads. When an angle wins, make an angle page whose first
screen repeats the ad's hook, for example "Unken tvätt trots att du har testat allt?" for pet homes
and "Därför luktar tvätten mögel" for the mold angle. Check that the offer on the page matches the
ad.

## Learnings so far (dated)
- 2026-11-04: First labels (Meta + Trackpanda, last 30 days). **B11 (C2 in "ny batch 4") is a
  breakthrough**: ~76 % of its CBO's spend, CPA 82.5 kr vs the account's 124.5 kr, Trackpanda ROAS 6.4.
  Next best: C8 in batch 3.1 (driveway teardown, ROAS 4.7), C3 in batch 3 (B04 biofilm footage, KPI
  winner, ROAS 4.1), C3 in batch 1 (pipes, spend winner, ROAS 2.3). Pattern: every top ad is a long-form
  technician teardown story, so third-person authority plus visual proof is our strongest component
  so far. First iteration: B12 (I1-B11).
- Product shots for end cards: the shop's product images (Shopify product "MASKINRENT - Maskinvård för
  tvättmaskiner") work as clean pack shots in place of Uproot's product section.
