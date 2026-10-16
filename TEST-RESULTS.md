# Test results: v5 (Sprint 02)

Automated browser tests on 16 Oct 2026, in three set-ups:
- desktop at 1440×900 with 3D
- phone at 390×844 with 3D
- laptop at 1280×800 with 3D graphics switched off (flat-map fallback)

**84 of 84 checks passed.** There were no script errors and no sideways scrolling in any set-up.

| Acceptance criterion | Result | How it was checked |
|---|---|---|
| 1. Village landing page works | Pass | Search "patamea" → Enter village → landing opens, link becomes #patamea |
| 2. Both pathway buttons work | Pass | Explore the Village and Discover Our Stories each open their view |
| 3. Explore the village spatially | Pass | Perspectives, location list, map markers, location card, Places list (5 unpinned slots), Gallery (6 slots) |
| 4. Browse village stories | Pass | Story grid renders; detail opens from cards and from map cards |
| 5. Switch between both experiences | Pass | Story → See on the map → place card opens; Back returns to Stories |
| 6. Village context retained | Pass | Switch to Le‘auva‘a and back: Patamea's depth setting and filters are kept |
| 7. Categories and filters function | Pass | All 6 categories open; category and format filters narrow results; empty state appears |
| 8. Media with fallbacks | Pass | Every media slot shows a labelled placeholder; no-3D devices get the flat map |
| 9. Mobile and desktop layouts | Pass | Bottom-sheet explorer on phones; screenshots included |
| 10. Accessibility alternatives | Pass (partial, see below) | List view of all places, keyboard tabs, Escape key, focus moves to each new heading, reduced motion stops camera flights and orbit, captions and transcript toggles |
| 11. Cultural placeholders identified | Pass | Every story, place slot and listing carries a status label; restricted items are counted but never shown |
| 12. Existing functionality preserved | Pass | Arrival, island search, journeys, list view and Stories library still work |
| 13. Implementation tested | Pass | This report |
| 14. Ready for Creative Director review | Pass | Live preview link and this folder |

## Not yet verified
- A full WCAG 2.2 AA audit with a screen reader (VoiceOver or NVDA) by a person. The automated checks above do not replace it.
- Colour contrast of small text over the moving 3D background, on a range of real phones.
- Performance on low-end Android phones on slow connections. The page is about 330 KB before fonts and the 3D engine.

# Sprint 03: Village Heritage

`python -m unittest discover -s tests -v`: **25 of 25 passed** on 16 Oct 2026, including the 4 browser rendering tests.
The 84 Sprint 02 checks were re-run against the new build: **84 of 84 passed**.

| Area | Tests |
|---|---|
| Historical association | name match alone rejected; village and district rules; unknown evidence rejected; levels kept distinct; a village claim backed only by a district link becomes "uncertain" |
| Permissions | each publication gate blocks on its own (rights, research status, publication status, approver, sensitivity, page reference, source); uncertain entries need explicit approval; publication scope limits what text is built |
| Import format | imports are always unpublished and restricted; blanks are never guessed; invalid values rejected |
| Public build | research folder never reaches the public build; an unapproved file in the approved folder stops the build; approved entries need confirmed rights; empty profiles build for Patamea and Le‘auva‘a |
| Repository guard | `research/` is git-ignored; every tracked approved record passes the rules; committed `index.html` matches a fresh build |
| Rendering | empty states and Te Papa citation on both villages; three views and keyboard tabs; village, district and uncertain groups render separately using fictional fixtures; name-match-only entry is not linked; no sideways scroll on phones |
