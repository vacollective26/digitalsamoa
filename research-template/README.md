# Research import: indexing historical sources

This folder holds **templates only**. Real research material goes in `research/`,
which git ignores, so it never reaches GitHub or the public site.

## Before you start
1. **Rights.** Te Papa labels the 1981 *O le Tusi Fa‘alupega o Samoa* (FE012543) as
   "No Known Copyright Restrictions". That is Te Papa's assessment, not a licence.
   Confirm the intended use with Te Papa (and, ideally, the publisher) before anything is
   published. Then set `rights.confirmedForUse` to `true` in `data/heritage/sources.json`,
   with a note of who confirmed it and when. Until then, the build publishes nothing from the source.
2. **Cultural authority.** Fa‘alupega are held knowledge. Agree with village and district
   authorities how entries are reviewed, who approves them, and how much may be shown.

## Indexing (research only)
1. Copy `faalupega-index-template.csv` to `research/index.csv`.
2. Add one row per entry as it appears in the book. Use:
   - `entry_id`: e.g. `tfs1981-p012-03` (source, page, order)
   - `printed_page` (the number printed on the page) and/or `pdf_page` (page in Te Papa's PDF)
   - `heading_as_printed`: the heading exactly as printed. Do **not** modernise the spelling here; put modern or alternate spellings in `variant_names`, separated by `;`
   - `level`: `village`, `district` or `uncertain`. If you're not sure, use `uncertain`.
   - `village_id` / `district_id` and their evidence, separated by `;`. Allowed values:
     `source-structure`, `second-source`, `community-confirmed`, `name-match`
   - Leave anything you don't know **blank**. Never guess.
3. Run `python tools/heritage.py import research/index.csv`.
   Every imported entry is **unpublished** and **restricted**.
4. Run `python tools/heritage.py check` to see what each entry still needs.
5. Optional: `python tools/build.py --research-preview` writes `research-preview.html`
   (git-ignored, watermarked) so researchers can see drafts in the site. Don't share it.

## Association rules (enforced in code)
- A **name match is never enough**. It is kept as a lead only.
- **Village** association needs `community-confirmed`, or both `source-structure` and `second-source`.
- **District** association needs `source-structure` or `community-confirmed`.
- Anything that doesn't meet the rule is shown (in research) as **uncertain**.

## Publishing (community-reviewed)
An entry can only be promoted when **all** of these are true:
- the source's rights are confirmed for this use
- `research.status` is `verified-against-source`
- `publication.status` is `approved`, with `approvedBy` and `approvalRef`
  (e.g. the date and record of the village meeting)
- `sensitivity` is `public`
- it has a page reference
- its level is valid (uncertain entries need an explicit `publishAsUncertain: true`)

`publication.scope` controls how much is shown: `citation-only` (default),
`summary`, or `full-text`.

Then run `python tools/heritage.py promote <entry_id>`, then `python tools/build.py`,
review the site, and commit. The build re-checks every approved entry and stops if any fails.

## Withdrawal and correction
Delete the entry's file from `data/heritage/approved/`, rebuild and commit. It disappears
from the site and its search. Record the reason in the research copy.
