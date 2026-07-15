# FloodLens — Reported Flooding Handoff (for next agent)

Project root: `e:\CityCAT Analysis\CityCAT_2026\Flood Risk Tool_New`
Open `index.html` in a browser (most report photos/MyCoast need internet).
Key files: `app.js`, `index.html`, `styles.css`, `data/reports.js`, images in `images/reports/`.
Rebuild data offline with: `python _rebuild_all.py` (NO live geocoding — uses a hardcoded coord table).
Source inputs: `E:\CityCAT Analysis\CityCAT_2026\Flooded Locations\` (KMLs, two .txt notepads, PPTX).

## LATEST SESSION — what was done (2026-07)
- **Photos rebuilt offline** from the CURRENT `images/reports/` folder via `_rebuild_all.py`.
  No Nominatim (it throttled before). Every distinct location has hardcoded (lat,lng).
  Duplicate names merged into ONE marker (e.g. Frederick Ave + Frederick_Ave +
  "5000 BLOCK OF FREDERICK AVENUE"; Fells Point + Thames St; Aliceanna + Caroline + S Caroline;
  35th & Hillen + E 35th + 1700 E 35th; Ellicott City + Main St Ellicott City).
  Result: **26 photo locations** (FLOOD_REPORTS). Deleted "dry area" photos are simply
  no longer in the folder, so they dropped out automatically. Leftover PPTX slide exports
  (`s02_2.jpg` … no location) are ignored by the rebuild.
- **Videos** attached per location in `data/reports.js` (`videos:[...]`), and shown in BOTH the
  marker popup ("▶ Watch flooding videos here") and the gallery. Wired:
  Ellicott City, Fells Point, Aliceanna St, Frederick Ave, Glen Burnie (TikTok),
  Davis/Gorman/Foundry Laurel (Facebook).
- **Report markers now show outside the Beltway** (Ellicott City, Glen Burnie, Laurel, Joppa,
  Towson, etc.) — `drawReports/drawSocial/drawMyCoast` no longer filter by `inBeltway`.
- **MyCoast**: removed the out-of-area beach/tidal point (lat 39.184, off Dundalk) and any
  point south of 39.19. MYCOAST now 26 (was 27). Tidal/beach already excluded by bbox.
- **Road closures**: rebuilt as their own layer (⛔ red) from the notepad — 31 points, deduped.
- **Social & newsletter**: kept existing 130 + appended 6 new notepad lines (deduped) = 136.
  YouTube points (23) still shown within the Social layer. NEWS layer stays retired/empty.
- **Lightbox upgraded**: click photo (or +/−, scroll wheel, on-screen zoom buttons) to ZOOM,
  drag to pan, big "NEXT ›" arrow with label, ‹ prev, counter, keyboard ← → + − Esc.
  Gallery thumbnails enlarged (min 320px, up to 340px tall) so photos aren't tiny.
- **Address search improved**: more county suffixes (Howard, Anne Arundel, Harford, Ellicott City),
  widened accept box (covers Ellicott City / Laurel / Silver Spring / Harford Co.), and a LOCAL
  gazetteer fallback built from all report/social/closure names + common town aliases, so town
  and street names resolve even when the online geocoder fails or is rate-limited.

## Current counts
FLOOD 26, SOCIAL 136, YOUTUBE 23, MYCOAST 26, CLOSURES 31, NEWS 0.

## How the app reads it
`app.js` defines REP/SOC/YT/MYC/RCL from those consts, `repMarker()` builds popups + gallery,
`openGallery()`/`openLightbox()` handle photos+videos+zoom, `drawReports/drawSocial/drawMyCoast/
drawClosures` render layers, toggles wired via `lyr("lReports"|"lSocial"|"lMyCoast"|"lClosures", ...)`.
Gallery modal markup is `#galModal` in index.html; lightbox is created dynamically (`#lightbox`).

## To re-run the data build after adding/removing photos
1. Add photos to `images/reports/` named by location (e.g. `Frederick Ave_9.png`). Remove any
   dry-area photos from the folder.
2. If a NEW location isn't in the table, add it to `GROUPS` in `_rebuild_all.py` with its
   coords + filename alias(es) (and `videos` if any).
3. Run `python _rebuild_all.py`. It rewrites `data/reports.js`. Reload `index.html`.

## Still optional / TODO for next agent
1. TikTok/Facebook/YouTube inline embeds instead of just links (currently open in a new tab).
2. Confirm a couple MyCoast points near water aren't tidal.
3. Do NOT batch-geocode via Nominatim — it throttles. Use the `_rebuild_all.py` coord table.

## MyCoast data source (street/pluvial only)
Live feed: `https://services1.arcgis.com/tikbh7xC3WJpzTz6/arcgis/rest/services/currentFL_viewMD/FeatureServer/0/query`
Filter `Report_Type='Storm Reporter'`, require `ImageUrls`, bbox `-76.80,39.18,-76.45,39.45`
(Baltimore/Beltway core; excludes eastern beaches/tidal).
