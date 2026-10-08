# HTML→PNG UI Mockup Rendering — window height per page

When rendering UI mockups (ERP screens) to PNG for a docx FDD, the default
1280x720 window leaves big empty bands on short pages and TRUNCATES tall pages.

## Per-page window height (chrome --screenshot)

Short content pages (dashboard, list, detail, inbox): 1280x720 works, but if
the page content ends at ~530px you get a 25-30% empty white band. Fix by
EXTENDING the content (add a bottom row: pipeline bar-chart panel + activity
feed) rather than shrinking the page — fills the viewport with useful info.

Tall pages (create/edit forms with header card + line-item table + totals
footer + action buttons): content ~900-1000px, gets cut at 720. Pass the
height per page, e.g. `shot(name, height=1000)`.

Best practice: write the mockup generator so `shot()` takes a height argument
and the main script carries a per-page height dict:
`heights = {'dashboard':720, 'create_po':1000, 'login':700}`.

## Content-fill rule (what users call "berantakan")

Empty space at the bottom of a mockup reads as "messy/broken" in a client FDD.
Rules:
1. Header card + one table card is NOT enough for a 720px viewport — add a
   second content row (mini bar chart of document pipeline, activity feed).
2. Login screens: split panel 40% form / 60% hero gradient with large soft
   decorative circles — fills the width naturally.
3. Keep table footer bars + status lines so cards visually terminate.

## Chrome quirks

- `--screenshot` renders exactly `--window-size`; no auto-height. There is no
  headless "full content height" flag — per-page height is the control.
- Bell/emoji glyphs written as raw UTF-8 in the generator source can corrupt on
  write; use HTML entities (`&#128276;`) instead.
- Verify character integrity after generation: count U+FFFD replacement chars
  in the produced HTML before burning render time.
