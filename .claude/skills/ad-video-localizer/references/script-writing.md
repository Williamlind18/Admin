# Writing the new script

## What you need first
- **The original voiceover text.** Speech cannot be transcribed in the sandbox, so ask the user to paste
  it. Ad-library transcripts with timestamps every ~5 s are ideal: they also tell you roughly when each
  original line is spoken, which gives you starting points for the anchors.
- **The user's product facts:** brand and product name, what it does, pack size and duration, how to use
  it, prices and discounts, current campaign, guarantee, shipping, review score and customer count, and
  the target audience. Try WebFetch on their product page. Store domains are usually blocked in the
  sandbox and brand-new shops are not indexed by search, so ask for **screenshots** and read them with
  the Read tool.
- **What must stay.** Ask which original lines or claims must stay. Once the user says a line stays, it
  stays.

## How to write it
- **Aim for natural spoken target language, not literal translation**, unless the user explicitly asks
  for a direct translation. Keep the hook, the story beats and their order, because the footage was cut
  to them.
- **Swap every competitor/brand reference** for the user's brand, product name and facts. Only state
  facts that are on the user's page. Never invent prices, guarantees, review scores or safety claims.
  If an original claim (e.g. "septic safe") isn't on their page, ask before including it.
- **Keep deictic lines tied to their footage** ("this", "here's how it looked", "and now"). Find those
  moments on the contact sheets and write them down. They become anchors in `plan_timeline.py`. Put
  the pointing word at the **end** of the sentence ("Det gick så långt att jag fick det här."), then
  anchor the sentence's end to the moment it should hit.
- **Put one sentence per line.** Keep lines short (≤ ~15 words) because they sync better. A long list
  sentence can be fine, but it is one block.
- **Write numbers as words** for TTS (see elevenlabs.md).
- **Common ad structure** (a map, not content): hook → problem → cause explained → consequence or proof
  → discovery of the product → how to use it → what it does → result → before/after → who it's for →
  product facts and guarantee → offer and urgency → call to action.

## Length budget (check before spending credits)
`split_script.py … --video-duration D` estimates the speech length. Rules of thumb:
- eleven_v3 Swedish runs at about **16 characters per second** (spaces included). The script must fit
  in `D − 0.35 − 0.18 × (lines − 1)` seconds at ≤ ~1.08× speed.
- **The ending is where it breaks.** The offer and call to action usually come after the last visual
  anchor, and only the seconds after that anchor are available for them. Check that section on its own:
  `chars_after_last_anchor / 16 ≤ seconds_after_last_anchor × 1.10`. If it doesn't fit, move generic
  lines (e.g. "Har du husdjur? …") in front of the anchored lines, or tighten the offer wording.
  Optional extras the user asked for "if it fits" (review scores, customer counts) are the first things
  to drop. Tell the user you dropped them.
- If the original ad had long passages you condensed, the voice will run ahead of the pictures and
  leave gaps. Restoring detail (e.g. names the user wanted kept) is a good way to fill them.

## Before generating: show the full script
Show the user the complete script, numbered like the files, and get a go-ahead. Credits are spent per
character. In the same message, flag once (don't lecture):
- Health or medical claims, and "my doctor said…" style testimonials when the voice is AI and the story
  is invented. These can count as misleading marketing (in Sweden, marknadsföringslagen).
- Hard deadlines ("ends tonight") in a video that will run for weeks.
- Competitor branding visible in the footage while the voice names the user's brand.

The user decides. Keep what they want and don't quietly remove or soften it.
