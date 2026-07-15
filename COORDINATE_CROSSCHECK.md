# Coordinate crosscheck — July 15, 2026 (v2)

> **v2 note:** `_rebuild_all.py` had been re-run with its old hardcoded table, which reverted the v1
> fixes and dropped the renamed photos. Both `data/reports.js` AND the script's GROUPS table now carry
> the corrected coordinates, the new aliases for the renamed files (Oella Avenue, I-695 near Glen Burnie,
> Baltimore Beltway & Greenspring Ave, Hilton Parkway and Edmondson Avenue, Dunkin' 458 N Camp Meade Rd,
> Broadway Street East), so re-running the script is now safe. Additional v2 coordinates:
> N Camp Meade Rd now at the Dunkin' (458) at 39.214788, -76.644027; Beltway & Greenspring at the
> I-695/Greenspring Ave interchange 39.395973, -76.688217; I-695 near Glen Burnie at the I-695/I-97
> junction 39.202447, -76.631627; Oella Avenue at 39.26992, -76.774681; Westchester Ave placed on the
> street beside the modeled flood area at 39.2710, -76.7862 (per LJ's screenshot).

Method: every suspicious entry in `data/reports.js` was geocoded against the Esri World Geocoder
(findAddressCandidates, score ≥ 99 unless noted); 311 service points were sampled and compared
to their own Address field. Distances are approximate.

## 311 reports (live Open Baltimore layers) — OK, no change
Sampled points all land exactly on their tooltip addresses (e.g. 3712 Chestnut Ave, Boarman & Reisterstown,
605 S Bradford St, Bolton & McMechen, Calvert & Fayette, 6701 Duluth Ave). The city geocodes 311 calls to
the block/intersection level, so a dot can sit at the middle of a block rather than the exact puddle —
that is source precision, not a plotting error.

## Fixed in data/reports.js (old → new)

| Entry | Was | Now | Error |
|---|---|---|---|
| FLOOD "Frederick Ave" (photos are 5000 block) | 39.2846, -76.6706 | 39.281391, -76.696971 | ~2.3 km |
| FLOOD "Hilton St & Edmondson Ave" | 39.29, -76.669 | 39.294392, -76.672742 | ~0.6 km |
| FLOOD "North Point Rd & Kane St" | 39.2637, -76.499 | 39.296976, -76.529749 | ~4.5 km |
| FLOOD "1901 Falls Road" | 39.3193, -76.6438 | 39.311552, -76.620157 | ~2.2 km |
| FLOOD "N. Camp Meade Rd, Linthicum" | 39.2065, -76.665 | 39.208234, -76.651582 | ~1.2 km |
| FLOOD "Timonium & Greenspring Ave" | 39.439, -76.647 | 39.438903, -76.631414 | ~1.3 km (see note) |
| FLOOD "Westchester Ave near Frederick Rd" | 39.279, -76.73 | 39.267349, -76.793103 | ~5.6 km |
| FLOOD "921 E Fort Ave" | 39.270522, -76.5979 | 39.271207, -76.600684 | ~0.25 km |
| FLOOD "6500 block of E Lombard St" (+ matching YouTube entry) | 39.295586, -76.533188 | 39.29674, -76.534468 | ~0.17 km |
| ROADCLOSURE "Mount Washington at 5910 Falls Rd" | 39.379868, -76.655937 | 39.369478, -76.649154 | ~1.3 km |

Note — Timonium: there is no "Greenspring Ave" at Timonium; the geocoder (and the recurring flood
location) is Greenspring **Drive** at W Timonium Rd, which is what the point now uses. Rename if desired.

## Verified correct (spot checks, unchanged)
Ellicott City Main St; Fells Point / Thames St; Aliceanna & Caroline; 35th & Hillen; Towson;
700 N Eden St; Catonsville & Oella; Turner Station; Dundalk Ave @ Holabird; Smith Ave; Sawmill Creek;
Glen Burnie center point; SOCIAL Frederick Ave cluster (4800–5300 blocks); Mt. Washington 5910 Falls (SOCIAL);
Kelly Ave Bridge; Meadow Mill.

## Flagged — could not verify, left unchanged (review manually)
- FLOOD "East Broadway (Richford–Vinal)" at 39.305, -76.59: Baltimore has no *East* Broadway; Bel Air
  (Harford Co, outside the beltway) does, but the geocoder can't find Richford/Vinal there. Confirm the
  news source; the current pin sits on N Broadway in Baltimore City.
- FLOOD "Silver Spring (NE Baltimore)" at 39.39063, -76.488854: name suggests Silver Spring (Montgomery Co)
  but the pin is Perry Hall/White Marsh. Check the photo's original story.
- FLOOD "Spring Valley" at 39.413817, -76.644903: ambiguous place name; couldn't confirm.
- FLOOD "Glen Burnie (I-695)" — I-695 doesn't reach Glen Burnie (I-97/MD-2 does); pin is Glen Burnie
  center. Title may be wrong rather than the pin.
