# Iteration backlog for Maskinrent

Ready briefs in the `ad-iterations` format, with Swedish hooks. Pick by the latest labels. Before any
labels exist, this order makes sense:
1. **B11**, the Uproot grandpa ads. They are proven breakthroughs at Uproot and missing in our account.
2. **B06-I01**, Spencer's own suggestion: iteration 2 with an authority added.
3. **A format swap** of whichever ad labels best.

Show the user the brief and the full script before generating a voice. Check every hook against
"Claims that need the user's OK" in SKILL.md. Hooks with persona stories need the user's decision.

## B11-I00 – The grandpa (Uproot's original)
- **What:** a Swedish version of Uproot's grandpa ad. Solution aware, with grandpa as the authority.
- **Why:** Spencer's verified breakthrough. Grandpa authority is the one Uproot learning we have never
  tested. He says the authority tells what is wrong and recommends the mechanism, not the brand.
- **How:** the user finds the ad in Uproot's Ad Library and uploads it as the next release (video48).
  Produce it with `ad-video-localizer`. The script follows the beats in `uproot-breakdown.md`.
- **Hooks:**
  - H1 (authority): "Min morfar lagade tvättmaskiner i hela sitt liv. Det här sa han att jag skulle
    göra åt lukten."
  - H2 (urgency): "Du tvättar inte kläderna, du långkokar dem i mögel. Det sa morfar efter en enda
    sniff."
  - H3 (unaware): "Visste du att de flesta tvättmaskiner möglar inuti, fast tvätten ser ren ut?"
- **Check:** a grandpa told by an AI voice is a persona story. Flag it once.

## B11-I01 – The grandpa, status version (Uproot's iteration 1)
- **Changes from B11-I00:** avatar broad (anyone who never cleans the machine), desire status,
  awareness problem aware. Urgency tied to the story, but only if it is true.
- **Inherits:** the grandpa, the angle, the mechanism.
- **Hooks:**
  - H1 (problem aware): "Har du aldrig rengjort din tvättmaskin blir det här obekvämt att höra."
  - H2 (status): "Kollegan frågade om mina kläder alltid luktar så här. Jag ville sjunka genom golvet."
  - H3 (authority): "Min morfar sa alltid att tvättmaskiner är riktigt smutsiga inuti. Jag trodde inte
    på honom."

## B06-I01 – Mold with an authority
- **Parent:** B06 (Uproot iteration 2).
- **Changes:** add a third-person authority (technician or laundromat owner) and name the three
  enzymes, because B06's mechanism is vague.
- **Inherits:** the mold urgency first, the three-mistakes list, the unaware opening, B06's footage.
- **Hooks:**
  - H1 (urgency, inherited): "Så långkokar din smutsiga tvättmaskin kläderna i mögel, särskilt om du
    har husdjur."
  - H2 (authority): "Jag har lagat tvättmaskiner i nitton år. Här är tre misstag som får din maskin
    att mögla."
  - H3 (inversion): "Tre varningstecken på att din tvättmaskin möglar inuti."

## B04-I01 or B10-I01 – Did you know (awareness down)
- **Parent:** the better labeled of B04, B07 and B10.
- **Changes:** awareness from problem or solution aware to unaware; higher intensity in line one.
- **Inherits:** the authority, the story, the mechanism, the offer.
- **Hooks:**
  - H1: "Visste du att det finns ett utrymme i din tvättmaskin som aldrig blir rent?"
  - H2: "Bakom trumman i din tvättmaskin bor det något. Det är därför handdukarna luktar."
  - H3: "Din tvättmaskin har ett dolt utrymme som ingen rengöring når."

## Desire switch to status
- **Parent:** B04 or B10.
- **Changes:** desire from health or money to status (others notice the smell). The avatar's emotion
  becomes embarrassment.
- **Hooks:**
  - H1: "Gästerna sa ingenting. Men jag såg att hon luktade på handduken."
  - H2: "Det pinsammaste med husdjur är inte håren. Det är lukten i tvätten som alla utom du känner."
  - H3: "Luktar dina kläder blöt hund? Alla runt dig märker det före dig."

## Desire switch to money
- **Parent:** B10 (already leans on "don't scrap the machine").
- **Changes:** lead with the cost of a new machine. Keep the teardown proof.
- **Hooks:**
  - H1: "Innan du köper en ny tvättmaskin, titta bakom panelen på den gamla."
  - H2: "Hon skulle skrota en tre år gammal tvättmaskin. Det var inget fel på den."
  - H3: "Din tvättmaskin är inte trasig. Den är smutsig där du inte ser."

## Mechanism short ads
- **Parent:** B09.
- **Changes:** three hooks for the 15-20 second mechanism format. Each enzyme stays tied to its
  benefit.
- **Hooks:**
  - H1: "Djurhår är protein. Därför biter inte vanliga maskinrengörare på dem."
  - H2: "Tre enzymer, tre jobb. Så får du bort lukten ur tvättmaskinen."
  - H3: "Ättika och blekmedel sköljer över beläggningen. Enzymer löser upp den."

## Inversion of the UV test
- **Parent:** B03.
- **Changes:** list format and inversion; awareness down.
- **Hooks:**
  - H1: "Tre tecken på att tvätten inte blir ren, fast den luktar okej."
  - H2: "Luktar handduken okej? Titta på den under UV-ljus först."
  - H3: "Det här lyser på en handduk som precis kommit ur tvätten."

## Format swaps (any labeled winner)
Inherit the script and change only the visuals:
- **AI-animated explainer:** the three enzymes animated attacking the film, the hair and the fat.
  Generate B-roll with the ElevenLabs or Higgsfield connector after confirming the cost with the user.
- **Podcast clip:** two voices discussing the problem.
- **Text-on-screen list:** the three mistakes as large text over B-roll.
- **Static or carousel:** an offer ad with the `bof-offer-ads` skill.

## Story-tied urgency (only if true)
Replace "medan erbjudandet gäller" with a reason from the story, for example "Sedan fler börjat titta
bakom panelen har vi haft svårt att hålla lagret". Ask the user whether it is true before using it.
