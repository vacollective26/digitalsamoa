# Sāmoa Digital: concept prototype, version 5 (Sprint 02)

Live site (once GitHub Pages is on): https://vacollective26.github.io/digitalsamoa/
Private review copy: https://claude.ai/artifact/6JFxZBxhGexKuwUGDAwFvX

This is a public prototype. Do not add real community stories, recordings, photographs or personal details to this repository until they have been approved for publication.

## Open it
- Visit the live site above, or download this repository and double-click `index.html`. It opens in Chrome, Safari or Edge, no installation needed.
- An internet connection is needed for the fonts and the 3D engine (three.js, loaded from cdnjs). Without one, the site falls back to system fonts and a flat map.
- Useful links (add to the end of the address):
  - `#arrival`: always play the opening
  - `#map`: go straight to the island explorer
  - `#patamea`, `#patamea-explore`, `#patamea-stories`, `#patamea-history` (also `people`, `culture`, `places`, `life`, `connections`)
  - `#leauvaa` works the same way
  - `#stories`: the cross-village stories library

## What is real
- Coastline: Natural Earth 1:10m (public domain).
- Elevation: SRTM-derived terrain tiles (AWS Open Data), on a grid of about 275 m, shown with heights ×2.5.
- Village coordinates and districts: public records (Wikipedia), still to be confirmed with each village.
- Place facts (Apia, Faleolo, Mulifanua, Salelologa, Silisili): public sources, cited in the site.
- Distances: calculated great-circle distances.

## What is simulated or a placeholder
- Every story, person, photograph, panorama and business listing is a labelled placeholder or fictional example.
- The story player steps through interview prompts; there is no recording.
- "Hear the name", 360° views and gallery images are slots awaiting contributions.
- Selecting SM (Gagana Sāmoa) explains that translations are pending review; no Samoan text has been written.
- The village introduction ("A village shaped by land, ocean and people") is draft copy from the design reference, labelled as awaiting village approval.

## Content model (in the `DATA` object inside index.html)
- **Village**: id, name, alternate spellings, island, district, coordinates, public facts, source, partnership status
- **Story**: id, category, media type, story type, depth level, duration, title, description, contributor credit, language, captions and transcript, associated location, permission record
- **Location**: generated per village. The recorded village point, the nearest coastline (calculated), and public places within 40 km. Each has its source. Places inside a village are listed as unpinned slots until the village agrees.
- **Business**: category slots plus two fictional examples (community listing and paid promotion), labelled as such
- **Cultural permission**: audience (public or restricted), status, consent, authority, allowed reuse. `Perm.isPublic()` is the only gate; restricted records never reach a page, a list or the search index.

## Moving to Next.js later (when there's a reason to)
1. Move `DATA` into JSON files (one per village) or a CMS such as Sanity. The shapes above become the schemas.
2. Split the script into React components along the existing section comments (map, explorer panel, journey, village landing, explore, stories, categories, story dialog).
3. Replace the hand-built 3D map with MapLibre GL JS and free terrain tiles, keeping the same camera views.
4. Host on Vercel or Netlify (free tiers are enough for a prototype). Each change gets its own preview link.

## Version control (recommended)
1. This repository (`vacollective26/digitalsamoa`) is the single source of truth.
2. Keep three files at the top: `index.html` (the site), `DECISIONS.md` (the decision register, IDs as approved by the Creative Director) and `CHANGELOG.md`.
3. Each sprint gets its own branch (`sprint-03-...`). Connect the repository to Netlify or Vercel so every branch has its own preview link. Merge only after the Creative Director approves.
4. To share with another AI conversation, attach `index.html`, `DECISIONS.md` and the latest design brief. Never rely on a sandbox link.
5. Tag each approved release (`v5`, `v6`…) so any earlier version can be restored.
