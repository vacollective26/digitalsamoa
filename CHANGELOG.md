# Changelog

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
