# Templates

Write these in the user's language. The headings below are English; translate them (Swedish:
Komponentkort, Memo, Iterationsbrief, Batchplan, Fredagsrapport).

## Component card
```
Ad: <name, e.g. B04-I00>   Box: <Breakthrough / Spend winner / KPI winner / Loser / Too early>
Numbers: <spend, share of spend, CPA or ROAS, days running, budget change>

| Component   | What it is in this ad | Line that carries it | Strength |
|-------------|-----------------------|----------------------|----------|
| Angle       |                       |                      | strong / weak / missing |
| Avatar      | experiences / behaviors / emotions |          |          |
| Desire      |                       |                      |          |
| Mechanism   |                       |                      |          |
| Authority   |                       |                      |          |
| Awareness   |                       |                      |          |
| Emotion     | valence, intensity    |                      |          |
| Positioning |                       |                      |          |
| Urgency     |                       |                      |          |
| Format      | (not one of the nine, but record it) |       |          |

Why it is in its box (hypothesis): <which components drive or block it>
Confidence: <low / medium / high, and why>
```

## Memo (every ad, before the script)
```
What:  <one sentence: the ad, its format and its angle>
Why:   <the learning it inherits, from which ad, and the hypothesis we test>
How:   <format, authority, hook approach, footage, length, landing page>
```

## Iteration brief
```
Name:    B<batch>-I<iteration>   Parent: B<batch>-I<n>   Box of parent: <…>
Memo:    What / Why / How (as above)

| Component   | Parent | This iteration | Inherited? |
|-------------|--------|----------------|------------|
| …nine rows… |        |                | yes / changed |

Hooks (same concept, different lead component):
  H1 (<component>): "<line>"
  H2 (<component>): "<line>"
  H3 (<component>): "<line>"

Script: <full draft, one sentence per line>
Format and visuals: <…>
Landing page: <evergreen / angle page; first-screen headline>
Claims to check: <anything that needs proof or the user's OK>
```

## Batch plan (one breakthrough)
```
Parent: B07-I00 (Breakthrough, 41 % of spend)
Learning: <the components we believe drive it>

| Name   | Changes                         | Inherits                | Hooks |
|--------|---------------------------------|-------------------------|-------|
| B07-I01 | authority: X → Y               | angle, mechanism, urgency | 3   |
| B07-I02 | awareness down ("Did you know") | authority, mechanism     | 3   |
| B07-I03 | desire: health → status         | authority, angle         | 3   |
| B07-I04 | format: AI-animated             | everything else          | 1   |
```

## Friday report
```
Week <nr> – <brand>

1. Labels (ads older than 7 days)
   | Ad | Box | Share of spend | KPI | Days | Note |

2. What we learned
   - Winning components: <component + evidence, e.g. "authority via list format wins in 3 of 4 ads">
   - Losing components: <…>
   - Surprises: <…>

3. Action items
   - Next batch: <names + one line each>
   - Format swaps: <…>
   - Landing pages: <…>
   - Stop: <ads to turn off or approaches to drop>
```

## Brand file (one per brand)
Keep it in `.claude/skills/<brand>-iterations/SKILL.md` with a description that names the brand and
products so it loads together with `ad-iterations`.
```
Brand and products: <names, markets, languages>
Product facts: <what it does, how to use it, pack size, duration>
Mechanism: <ingredients/features, each with its benefit>
Positioning: <what makes it different>
Offer: <current offer, price per unit, shipping, guarantee>; date checked: <…>
Claims we may use: <customer count, rating, origin story…, each with its source>
Claims to avoid: <…>
Competitors and their top ads: <names, what they do well>
Ad catalogue: <batch number, name, files, component summary, box>
Learnings so far: <dated bullets>
Iteration backlog: <ready briefs>
```
