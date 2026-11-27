# Meta ad structure: Ad account 3 (export 2026-11-27)

A full export of the five live campaigns in Ad account 3 (516758837558365, SEK, Europe/Stockholm), taken on
2026-11-27 while the account was restricted for business verification. The export has every campaign, ad set and
ad with their settings, so any of them can be rebuilt identically on another ad account. It holds structure and
settings only: no spend, profit or customer data.

| Campaign | Id | Ad sets | Ads | Budget in Ad account 3 | Floors |
|---|---|---|---|---|---|
| CBO - Maskinrent | 120251844607370505 | 26 (21 active) | 103 | 14 400 kr/day | 9 ad sets, 1 560 kr/day |
| CBO - Norrtvätt SE - BLACK WEEK | 120252767909710505 | 3 | 27 | 1 000 kr/day | none |
| CBO - Norrtvätt NO | 120252801527820505 | 6 | 32 | 1 440 kr/day | 2 ad sets, 340 kr/day |
| CBO - Norrtvätt DK | 120252954376960505 | 5 | 33 | 1 000 kr/day | none |
| BOF - Maskinrent | 120252105207900505 | 1 | 32 | 1 000 kr/day | none; COST_CAP 150 kr per purchase |

## Files

- `struktur.json` is the compiled structure: campaigns, then ad sets (full `targeting`, `promoted_object`,
  `attribution_spec`, floor, cost cap, brand safety), then ads (primary text, headline, link, `url_tags`, CTA, post
  id, IG media id, page, IG account, video and image ids, `asset_feed_spec`, AI enhancements on and off). Amounts
  ending in `_ore` are in öre (divide by 100); the `_kr` fields are already in kronor.
- `struktur.xlsx` is the same data as sheets: Kampanjer, Annonsgrupper, Annonser, Kontobundet (what must be shared to
  a new account) and Kontroll.
- `raw/<campaign>/` holds the original API answers: `campaign.json`, `adsets.json` and `ads.json` from Ark
  `get_meta_ads`, and `creatives*.json` from Meta `ads_get_creatives` (with `object_story_spec`, `asset_feed_spec`
  and `degrees_of_freedom_spec`). The only edit is that `budget_remaining` was removed.

## Settings shared by every ad set

- Objective OUTCOME_SALES. Optimisation OFFSITE_CONVERSIONS on pixel 1262459122680812, event PURCHASE. Billing
  IMPRESSIONS.
- Attribution: 7-day click, 1-day view and 1-day engaged view.
- Targeting: the market's country (home, recent and frequently in), age 18-65, all genders, Advantage+ audience on.
  No custom audiences, lookalikes or exclusions.
- Advantage+ placements. Natives C2, C4 and C9 (CBO NO A2 C5 and BOF "ny batch 2 - C6" too) use
  placement-customised creatives (`asset_feed_spec`, PLACEMENT).
- Campaigns: CBO, LOWEST_COST_WITHOUT_CAP, except BOF, which is COST_CAP. Ad sets have no budget, spend cap or end
  date.
- Every ad uses an existing post (`effective_object_story_id`), so likes, comments and shares carry over. `url_tags`
  is `ad_id={{ad.id}}` and CTA is SHOP_NOW.
- AI enhancements: the `advantage_plus_creative` bundle is OPT_OUT and `standard_enhancements` OPT_IN, with
  per-feature settings that differ between ads. For example, `translate_voiceover` is on for 60 of 103 Maskinrent ads.
  Copy them per ad from `degrees_of_freedom_spec`.

## Account-bound items to share to a new ad account

- Pixel/dataset 1262459122680812.
- Pages and Instagram accounts:
  - Norrtvätt SE: page 1234301249776145, IG 17841423637282628. Used by Maskinrent (94 ads), Black Week and BOF.
  - Natives: page 1043755995490418, IG 17841437408817583. Used by 9 Maskinrent ads.
  - Nordvask: page 1376054285595884, IG 17841465525513228. Used by NO and DK.
- Video ids and image hashes belong to Ad account 3. They are not needed while the ads are built from post ids.
