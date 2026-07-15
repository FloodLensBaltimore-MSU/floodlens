# FloodLens Baltimore — Handoff for Next Session

Project files: `index.html`, `styles.css`, `app.js`, `data/geo.js` (BELTWAY + SUBWS), `data/images.js` (EMB base64 scenes).
Open `index.html` in a browser. Most layers need internet (USGS / MD iMAP / Open Baltimore / Census).

## Already done (verify, don't redo)
- Welcome: single CLOSE button, real flooded-street photo.
- Return-period / duration controls live under "Floodwater (modeled)" in Layers panel.
- Green infrastructure toggle in Layers panel.
- Building exposure counts moved into the map legend (right "Building exposure" panel removed).
- Hover tooltips are horizontal again.
- Cut-off areas only draw when Floodwater layer is ON.
- Emergency facility list: flooded/cut-off facilities sorted to top when flood is on; no flood status text when flood is off.
- Police naming helper `facTitle()` prefers place/neighborhood over district.
- Streams rewritten to clean USGS NHD vector lines (no arrows/points), clipped to Beltway.

## STILL TO FIX (priority order)

### 1. Buildings not recoloring inside FEMA zones
- Code exists: `loadFemaZones()`, `femaZoneAt()`, `FEMA_BCOL/FEMA_BLAB`, used in `renderBld()`.
- Problem: FEMA vector query likely returns nothing. Verify the live service:
  `https://mdgeodata.md.gov/imap/rest/services/Hydrology/MD_Floodplain/MapServer`
  - Confirm correct **layer id** for polygon flood zones and the real **field names** (FLD_ZONE / ZONE_SUBTY / SFHA_TF). Open the service `/query` in browser to check.
- Also confirm buildings are actually loaded where FEMA zones exist (buildings only load near flood seeds + when zoomed in).

### 2. Data still shows as a rectangle, not clipped to Beltway
- Server-drawn rasters (buildings/roads/FEMA/flood) render to a bbox rectangle.
- Need a real clip to the irregular BELTWAY polygon. Options:
  - Apply an SVG `clipPath` / CSS `clip-path` to the raster panes using the Beltway ring, OR
  - Re-add a polygon **mask** (world-with-Beltway-hole) but keep basemap visible (mask only the data panes, fill = transparent-to-basemap is hard; better = clip-path).
- Prior mask was removed because it hid the basemap. Clip-path is the correct approach.

### 3. StreamStats grid from local drive not showing
- File: `E:\Data\md_streamStats\md_streamStats\streamgrid.tif` (GeoTIFF).
- Browsers can't read a local .tif directly. Do ONE of:
  - Convert to XYZ/tiles (gdal2tiles) and add as `L.tileLayer`, OR
  - Serve the folder over a local HTTP server and load with **georaster** + **georaster-layer-for-leaflet**, OR
  - Convert to GeoJSON (gdal_polygonize / stream vectorization) and add as a vector layer.
- Add it alongside the existing USGS streams toggle.

### 4. Whole-Beltway coverage (currently Baltimore City only)
These use City-only sources; swap to county/state datasets covering all 5 counties in the Beltway study area (Baltimore City 510, Baltimore Co 005, Anne Arundel 003, Howard 027, Carroll 013):
- **Neighborhoods** (`NB_URL`, Open Baltimore CityView) → add county place/CDP boundaries (Census TIGER Places, or MD iMAP).
- **Socio-economic income/kids/old/pov** (`CSA_URL`, BNIA — city only) → use Census ACS tract data for all counties (or keep BNIA for city + ACS elsewhere).
- **walk/bus/car %** (`TRACT_URL`) already broadened to 5 counties — verify it actually returns data (check field names CT_P/PT_P/WL_P and the `COUNTYFP IN (...)` filter on that FeatureServer).
- **Hospitals, cooling centers, homeless shelters, public/charter/independent schools, nursing homes** (`INFRA_URLS`, mostly CityView) → add MD iMAP statewide equivalents (some already listed as `ST(...)` fallbacks; confirm they load).

### 5. Infrastructure point locations look wrong (esp. MTA bus stops)
- Verify each `INFRA_URLS` service returns points in correct lat/lng (some MD iMAP layers are Web Mercator; `fetchGeo` converts x/y — confirm outSR=4326 works).
- Bus stops: `BUS_BASE` = MD_Transit MapServer layer 9. Confirm layer 9 is bus stops and coordinates are correct; spot-check a known stop.

## Notes / gotchas
- Flood depths are still the **synthetic demo model** (`depthAt`), not CityCAT rasters.
- `beltwayBounds`, `inBeltway()`, `pipGeom()` already available for clipping/point tests.
- Panes: zIndex order in app.js (`flood, fema, streams, road, bldg, choro, bnd`, plus `mask`/`bndtop`).
- Test in a session with internet; open browser devtools Network tab to see which service queries return 0 features.
