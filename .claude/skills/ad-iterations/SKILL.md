---
name: ad-iterations
description: "Turn winning paid-social ads into more winners with a repeatable system: label every ad (Loser, KPI winner, Spend winner, Breakthrough) from share of spend, KPI after 7 days, budget scale and time; break winners, yours or a competitor's, into nine components (angle, avatar, desire, mechanism, authority, awareness, emotion, positioning, urgency); then write iteration briefs, hooks and scripts that inherit a learning, plus format swaps, three-hook tests, imitation ads, landing-page fit, naming and a Friday learnings report. Works for any brand. Use it whenever the user wants new versions, iterations or hooks from an existing ad, asks why an ad works, wants an ad or competitor breakdown, to label winners or plan the next test batch - also in Swedish: 'gör iterationer', 'iterera på annonsen', 'varför funkar annonsen', 'bryt ner annonsen', 'vilka annonser vinner', 'nästa batch', 'nya hooks', 'learnings'."
---

# Ad iterations

A system for making more winning ads on purpose instead of guessing. It comes from a keynote by Spencer
(Evolve), whose agency ran about $160M of Meta ad spend in one year. One telehealth brand went from
$30k/month at $600 CPA to $2.5M/month at $245 CPA with creative alone. Detailed notes on the talk:
`references/source-notes.md`.

The loop has three steps, plus production and a weekly review:

1. **Label.** Decide how much each ad is winning. Winning is a scale, not yes or no.
2. **Learnings.** Find *why* the winners win, in nine components.
3. **Iterate.** Make new ads that inherit a learning and change chosen components.
4. **Produce** the ads with the right tools and name them so the iterations can be tracked.
5. **Report** every Friday: what we learned and what we do next.

Why this works after Meta's Andromeda update: Meta rewards creative diversity. An iteration that only
swaps a few words of the hook is a surface iteration and Meta treats it as the same ad. An iteration
that changes deep components (authority, awareness level, desire, format) reads as a new concept
while keeping what already sells. Meta's own diversification ladder, shown in the talk, runs from least to
most differentiated: same concept in the same format → new concept in the same format → new concept in a
new format.

Talk to the user in their language (Swedish for the original user). Show component cards and briefs
before anything costs credits or money.

## Before you start: the brand file

Look for brand-specific notes first. They hold product facts, the offer, allowed claims, the ad
catalogue and earlier learnings. For Norrtvätt / Maskinrent use the `norrtvatt-iterations` skill
together with this one. If no brand file exists and the user will iterate on this brand again, offer
to create one from the template in `references/templates.md` (keep it in `.claude/skills/<brand>-iterations/`).

Never invent product facts, prices, review scores, customer counts or guarantees. Use only what the
brand file or the user's shop page states, and ask for anything missing.

## Step 1 – Label

Four variables decide how much an ad wins: **KPI** (CPA or ROAS), **spend**, **scale** (how much the
ad let the account raise its budget) and **time** (how long it keeps running). They give four boxes:

| | Below the spend threshold | At or above the spend threshold |
|---|---|---|
| **Hits KPI after 7 days** | KPI winner – results without spend | **Breakthrough** – gets spend and lets you raise the budget |
| **Misses KPI after 7 days** | Loser – a flop | Spend winner – spend without results |

The spend threshold depends on account size. Small accounts give their winners a bigger share:

| Account spend per month (USD) | Share of spend a breakthrough takes |
|---|---|
| 0–100k | 30–60 % |
| 100k–250k | 20–50 % |
| 250k–500k | 10–30 % |
| 500k–1M | 8–15 % |
| 1M–2M+ | 5–10 % |

Breakthroughs are what matter. A KPI winner that never gets spend does not scale anything. The
difference between a $50k and a $1M account is mostly the number of breakthroughs.

The share on the four-box slide is the ad's share of its **campaign's** spend ("camp spend"), read after 7
days. The Quick Win doc instead takes the ad's share of the whole **account's** spend over 30 days. Both are
useful; say which one you used.

How to label:
- Get ad-level numbers for the last 30 days. If the Meta Ads or Trackpanda connector is available,
  read them yourself (read-only, never change campaigns). Otherwise ask for an Ads Manager export.
- Run `scripts/label_ads.py` on the CSV or JSON. It computes share of campaign spend (or account spend
  with `--share-base account`), KPI, age and the box.
  See `references/labeling.md` for columns, currency conversion and edge cases.
- Give ads under 7 days "too early". In CBO testing, a KPI winner becomes a breakthrough only once it
  pulls spend in the scaling campaign.
- For competitors, use the Meta Ad Library (or Ad Spy sorted by shares). Ads that run for months and
  that the brand keeps making versions of are their winners.

## Step 2 – Learnings

Get the ad itself: the transcript or script, the on-screen text and the visuals (frames or a contact
sheet for video). Then fill a **component card** (template in `references/templates.md`):

| Component | Question it answers |
|---|---|
| Angle | What is the main reason given to buy? |
| Avatar | Who is it talking to, by experiences, behaviors and emotions (not demographics)? |
| Desire | Which core want does it tap: health, status, money, comfort, belonging, safety…? |
| Mechanism | How does the product work, tied to what the customer cares about? |
| Authority | Why should anyone believe it? Who says it, and what proves it? |
| Awareness level | Where does the ad start: unaware, problem, solution or product aware? |
| Emotion | Valence (pleasant to unpleasant) and intensity (low to high). |
| Positioning | Why this and not everything else? Different beats better. |
| Urgency | Why act now, and is the reason real? |

Definitions, scales, examples and the levers for changing each one are in
`references/components.md`. Read it before your first breakdown in a session.

When time is short, find the **big four**: angle, authority, unique mechanism and urgency.

Avoid surface learnings. "It's UGC", "great hook" and "low CPC" explain nothing. Translate each into a
component: "The hook works because a trusted third person (authority) names the problem in line one."

One winning ad is a hypothesis. When the same component wins across several ads, that is evidence.
Write down which components you believe drive the result, and say how sure you are.

## Step 3 – Iterate

**An iteration is a new ad that inherits a learning from an existing ad, usually to improve a
result.** Every brief names what is inherited and what is changed.

Change several components when the ad needs it. Changing exactly one variable often breaks the flow
of the ad, because marketing is creative flow more than lab science. Keep what the learnings say is
working.

**Every ad needs a clear authority.** This is Spencer's point, not a style choice: authority is the
component he highlights among the nine, it is one of the big four, and his Quick Win says that if you
can't identify one of the big four in your best ad, add it in. One authority switch in his talk took
$15k a day. Every brief must therefore name its authority: who says it and what proves it. If the
parent ad has none, adding one is the first change. The grandpa in the Uproot ad is only his example of
authority, not a template to copy. Any true authority works: a professional (technician, expert,
doctor), a demonstration, test or teardown on camera, real numbers or reviews, or an education bias
built through a list format. See the guardrail below: it has to be true.

Choose the move from the box:

| Box | What it tells you | Move |
|---|---|---|
| Breakthrough | Everything is working | Inherit the most. Make many iterations and format swaps. Switch authority, desire or awareness one batch at a time. |
| KPI winner | The message sells but does not reach | Keep angle, mechanism and offer. Change hook, format, awareness level (lower it) or emotional intensity. |
| Spend winner | Meta likes it but it doesn't sell | Keep hook and format. Strengthen authority, mechanism and positioning, and check the landing page matches. |
| Loser | Little to inherit | New concept, or an imitation ad of a competitor's top ad. |

The proven recipes, with how-to and example lines, are in `references/recipes.md`: authority switch,
awareness shift ("Did you know…?"), desire switch, intensity up, angle switch, urgency to the front,
story-tied urgency, inversion ("mistakes", "red flags"), mechanism-to-benefit, positioning by
difference, avatar broadening, format swap and imitation ads.

The first kind of script iteration in the agency's playbook is the **Components Rewrite**. Break the winner
down by the nine components, find what works, what can be optimized and how the same components can be
executed differently. Then test better versions of the **hook** (the opening that stops the scroll), the
**bridge** (the move from the hook into the body) and the **hold** (what keeps people watching).

Execute the iteration visually too. In the worked example, each spoken line has its own B-roll shot of
about 2 seconds with a small caption. The authority is shown on camera (an older man sniffing the washer).
A status iteration shows an office scene, and a list iteration uses a headline overlay and "MISTAKE #1"
labels.

For each iteration, write an **iteration brief** (template in `references/templates.md`):
1. Name and parent: which batch and iteration it builds on.
2. Memo: **what** the ad is, **why** we make it (the learning and the hypothesis), **how** we make it.
3. Component diff: the nine components, parent against new. Mark each as kept, changed or **inherited
   learning** (the talk's slides use grey, green and a green frame with "!!!!!"). Flag weak ones, such as a
   generic sales urgency.
4. Three hooks for the same concept, each leading with a different component.
5. The full script draft, and the format and visuals.
6. Landing page note: does the page's first screen match the new angle?

A useful batch for one breakthrough is three to five iterations that change different components,
plus one pure format swap.

**Hooks:** test one concept with three hooks. Make the hooks differ in component (one leads with
authority, one with urgency, one with an unaware "Did you know"), not just in wording.

**First breakthrough for a new brand:** test many different angles broadly to find a direction, then
go deep on the angle that works. Imitation ads speed this up: run the learnings process on
competitors' top ads, then make your own version with your product and facts. A community member who
reached $5M a month put it in this order: crack the unique mechanism until the audience believes it,
understands it and sees every alternative as out of play. Then find the main winning angle. Then build
concepts, starting with different formats, find a few winners and scale them.

## Step 4 – Produce and name

- Video with a voiceover: write the script here, then produce it with the `ad-video-localizer` skill.
  Put all three hook lines in the same voice take as the rest of the script so the voice matches.
- Static offer ads: use the `bof-offer-ads` skill if it is available.
- Name every ad so iterations can be counted. In the talk's scheme every new test gets the next free
  batch number, plus a pointer to its parent: "Batch#5 Iter#2-Batch#3" is batch 5, the second iteration
  of batch 3. Use `B12 | I2-B03 | angle | authority | awareness | format | H1`; a brand-new concept has no
  I part. Full scheme in `references/labeling.md`.

## Step 5 – Friday report

Every Friday, write the learnings report (template in `references/templates.md`). Include the labels
of everything older than 7 days, the components that won or lost, and the next batch with briefs.
Whoever made an ad does its learnings first, and the whole team (editors and media buyers too) adds
to them. If the user just talks through why they think ads work, organize it into the report.

## Guardrails

- **Authority must be true.** A real profession, a real test or real numbers, or a story clearly told
  as a story. Invented experts, doctors, reviews or customer counts can be illegal misleading
  marketing (Sweden: marknadsföringslagen). Flag it once and let the user decide.
- **Urgency must be real.** Tie it to the ad's story or to a real offer end. Avoid fake countdowns.
- **Health claims** need support. Flag them once.
- **AI people:** clearly-AI animation and AI B-roll are fine. Ads that pass an AI person off as real
  are risky, and Meta may start labeling AI ads.
- **Imitation ads** inherit a competitor's components, rewritten for the user's product and facts. Do
  not name competitors unless the user asks.

## Reference files

- `references/source-notes.md` – the talk in detail, with timestamps, the worked example and the Q&A.
- `references/video-tidslinje.md` – every second of the 45-minute video in 99 intervals: what is shown
  and what is said (Swedish). Use it to check an exact slide or quote.
- `references/labeling.md` – labeling data, the script, thresholds, currency and naming scheme.
- `references/components.md` – the nine components: definitions, scales, levers and examples.
- `references/recipes.md` – iteration recipes, format swaps, hook tests, imitation ads, landing pages.
- `references/templates.md` – component card, memo, iteration brief, batch plan, Friday report and
  brand file.
- `scripts/label_ads.py` – labels ads into the four boxes from a CSV or JSON export.
