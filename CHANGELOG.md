# Changelog

## v9 · Content safety (SD-CD-008)
- Patamea's transcription withdrawn from the public build. The History page now shows the bibliographic citation (1981 edition, Faalupega o Savaii, p. 23, entry "Patamea") with a **Community review pending** status. No text from the entry is shown.
- The research record has moved to private research storage (git-ignored `research/`, plus the project's private notes). Nothing was deleted.
- New rule: summaries and transcriptions need confirmed rights, community confirmation and a recorded cultural review. A Creative Director override can no longer publish text.
- New repository guard: the build and the tests fail if words from the withdrawn transcription appear in any tracked file.

## v8 · Patamea's fa‘alupega (SD-CD-007)
- Patamea's entry from *O le Tusi Fa‘alupega o Samoa* (1981, printed p. 23) is published in full under Our History → Historical Record, with page citation to Te Papa.
- The entry carries a visible note: published on the Creative Director's decision, not yet reviewed by Patamea, rights not yet confirmed.
- Source record now notes the title page's "All rights reserved" alongside Te Papa's assessment.
- Le‘auva‘a: whole book searched, no heading found; shown as "Searched · no entry identified" with a note asking someone who knows the village to check.
- Rules: bounded Creative Director override (SD-TD-007), mirrored in the browser, with tests.

## v7 · Sprint 03: Village Heritage engine (branch `sprint-03-village-heritage`)
- Village Heritage section in **Our History** with three views: Historical Record, Understanding Fa‘alupega, Living Community Knowledge.
- Source record for *O le Tusi Fa‘alupega o Samoa* (1981, Te Papa FE012543) with a clickable citation to the collection. Rights recorded as Te Papa's "No Known Copyright Restrictions" assessment, **not yet confirmed for this use**, so nothing from it is published.
- Data model: sources, entries, page references, village/district associations with evidence, variant names, provenance, research status, publication status and scope, sensitivity.
- Association rules: a similar name is never evidence; village and district levels are kept apart; anything short of the rules is "uncertain".
- Research-only import (CSV → `research/`, git-ignored), `check` and `promote` tools, and a research preview that is never committed.
- Public build (`tools/build.py`) only reads approved entries and stops if any fails the rules.
- Respectful empty states for Patamea and Le‘auva‘a (not yet searched in the source).
- 25 automated tests (rules, permissions, import, build exclusion, repository guard, rendering).
- Project now builds from `src/site.html`.

## v5 · Sprint 02: Living Village Experience (SD-CD-006)
- Village landing over the live 3D terrain: name, island, draft introduction, two equal pathways (Explore the Village, Discover Our Stories), guided-journey link, category strip.
- Explore the Village: perspectives (Village, Overhead, Coastline, Island, All Samoa), 3D on/off, slow orbit, location markers with cards, stories linked to places, Places list (text alternative), 360° and Gallery slots.
- Discover Our Stories: featured documentary, category and format filters, empty state, story cards with contributor, language, captions, place and permission; story detail with related stories and "See on the map".
- Category pages: Our History, Our People, Our Culture, Our Places, Life Today, Local Connections, each with depth levels.
- Shared navigation: breadcrumbs, section links, Back (remembers your previous view), village switcher, EN/SM toggle, Map button, Escape key, deep links.
- Context kept per village (depth, filters, explore tab, chosen place) when switching villages and returning.
- Fixes: low coasts flickered through the sea on some graphics hardware; no-3D devices and data-saver mode now get the flat map automatically.

## v4: Content build-out
- Public places, the three named journeys, Culture tab, Stories library, phone menu.

## v3: Real 3D terrain
- SRTM-derived elevation, 3D view, tilt and orbit controls.

## v2: Replay control and #arrival link

## v1: First build
- Design system, cinematic arrival, island explorer, search, guided journey, village page, permission gate.
