# -*- coding: utf-8 -*-
"""
Offline rebuild of data/reports.js for FloodLens (NO live geocoding).

* Scans images/reports/ for the CURRENT photos (fixes broken .jpg/.png
  references, drops photos the user deleted), groups them by location using a
  hardcoded name->(lat,lng) table, merges duplicate location names into ONE
  marker, and attaches flood videos per location.
* Rebuilds ROADCLOSURE_REPORTS from "Known City Flood-related road closures.txt"
  (hardcoded coords, de-duplicated) as its own layer.
* Keeps the existing SOCIAL_REPORTS / YOUTUBE_REPORTS, appends the NEW lines from
  "Social media & newsletter reports.txt" (de-duplicated by name).
* Keeps MYCOAST_REPORTS but removes the out-of-area beach/tidal point.
"""
import os, re, json, io

ROOT   = r"e:\CityCAT Analysis\CityCAT_2026\Flood Risk Tool_New"
IMGDIR = os.path.join(ROOT, "images", "reports")
REPORTS_JS = os.path.join(ROOT, "data", "reports.js")

# ---------------------------------------------------------------------------
# 1) VIDEO links (user-supplied) keyed by a simple location id
# ---------------------------------------------------------------------------
VID = {
    "ellicott":  ["https://www.youtube.com/watch?v=TJdSEZHlCZw",
                  "https://www.youtube.com/watch?v=aaSxyQdnVw4"],
    "glenburnie":["https://www.tiktok.com/@foxbaltimore/video/7660649204515163405"],
    "davis":     ["https://www.facebook.com/GerardJebaily/videos/1942719096522976/"],
    "fells":     ["https://www.youtube.com/watch?v=RpkU13AQZ-Y",
                  "https://www.youtube.com/watch?v=RRK5GF6bmng"],
    "aliceanna": ["https://www.youtube.com/watch?v=86FcO1H15fs"],
    "frederick": ["https://www.youtube.com/watch?v=U3RZ4vK-mi0&t=378s"],
}

# ---------------------------------------------------------------------------
# 2) PHOTO location groups: each has a display name, coords, the normalized
#    filename aliases that belong to it, and any videos. Duplicate location
#    names (e.g. Frederick Ave / Frederick_Ave / 5000 BLOCK OF FREDERICK AVE)
#    are merged into one marker.
# ---------------------------------------------------------------------------
GROUPS = [
    {"name":"Ellicott City (Main Street)", "lat":39.2673, "lng":-76.7983,
     "aliases":["ellicott city","main street ellicott city"], "videos":VID["ellicott"]},
    {"name":"Fells Point / Thames St", "lat":39.281985, "lng":-76.589855,
     "aliases":["fells point","thames streets"], "videos":VID["fells"]},
    {"name":"Aliceanna St / Caroline St (Fells Point)", "lat":39.283407, "lng":-76.596561,
     "aliases":["aliceanna st","caroline street and aliceanna street","south caroline street"],
     "videos":VID["aliceanna"]},
    {"name":"35th St & Hillen Rd", "lat":39.330976, "lng":-76.590586,
     "aliases":["35th and hillen rd","e 35th street and hillen road","1700 block of east 35th street",
                "35th and hillen rd 10.jpg"],  # covers the double-extension file "..._10.jpg.png"
     "videos":[]},
    {"name":"Frederick Ave (5000 block)", "lat":39.281391, "lng":-76.696971,
     "aliases":["frederick ave","5000 block of frederick avenue"], "videos":VID["frederick"]},
    {"name":"Pulaski Highway, Joppa", "lat":39.430075, "lng":-76.348142,
     "aliases":["pulaski highway in joppa","pulaski highway, joppa md"], "videos":[]},
    {"name":"I-695 near Glen Burnie", "lat":39.202447, "lng":-76.631627,
     "aliases":["695 in glen burnie","i-695 near glen burnie"], "videos":VID["glenburnie"]},
    {"name":"Davis Ave / Gorman Rd / Foundry St, Laurel", "lat":39.0993, "lng":-76.8483,
     "aliases":["davis ave. gorman rd. and foundary st"], "videos":VID["davis"]},
    {"name":"N Camp Meade Rd (458), Linthicum Heights", "lat":39.214788, "lng":-76.644027,
     "aliases":["400 block of n. camp meade road in linthicum heights",
                "dunkin', 458 n camp meade rd, linthicum heights, md 21090"], "videos":[]},
    {"name":"Oella Avenue near Frederick Rd", "lat":39.267781, "lng":-76.793711,
     "aliases":["catonsville and oella","oella avenue"], "videos":[]},
    {"name":"Hilton Pkwy & Edmondson Ave", "lat":39.294392, "lng":-76.672742,
     "aliases":["hilton near edmondson in southwest baltimore",
                "hilton parkway and edmondson avenue"], "videos":[]},
    {"name":"North Point Rd & Kane St", "lat":39.296976, "lng":-76.529749,
     "aliases":["north point road and kane street"], "videos":[]},
    {"name":"Baltimore Beltway & Greenspring Ave", "lat":39.395973, "lng":-76.688217,
     "aliases":["timonium at greenspring avenue",
                "baltimore beltway & greenspring avenue"], "videos":[]},
    {"name":"Towson", "lat":39.403455, "lng":-76.601859,
     "aliases":["townson"], "videos":[]},
    {"name":"Ruxton Road, Towson", "lat": 39.400949, "lng":-76.664987,
     "aliases":["ruxton road, towson","ruxton rd"], "videos":[]},
    {"name":"700 N Eden St", "lat":39.298261, "lng":-76.599047,
     "aliases":["700n eden st"], "videos":[]},
    {"name":"921 E Fort Ave (Locust Point)", "lat":39.271207, "lng":-76.600684,
     "aliases":["921 e fort ave"], "videos":[]},
    {"name":"1901 Falls Road", "lat":39.311552, "lng":-76.620157,
     "aliases":["1901 falls road"], "videos":[]},
    {"name":"6500 block of E Lombard St", "lat":39.29674, "lng":-76.534468,
     "aliases":["6500 block of east lombard street"], "videos":[]},
    {"name":"Dundalk Avenue", "lat":39.272579, "lng":-76.530858,
     "aliases":["dundalk avenue"], "videos":[]},
    {"name":"E. Eager St & N. Wolfe St", "lat":39.301996, "lng":-76.591118,
     "aliases":["e. eager st and n. wolfe st","eager st"], "videos":[]},
    {"name":"Fulton Ave", "lat":39.311122, "lng":-76.646821,
     "aliases":["fulton ave"], "videos":[]},
    {"name":"Light St & E. Pratt St (Inner Harbor)", "lat":39.286690, "lng":-76.613071,
     "aliases":["light and e. pratt"], "videos":[]},
    {"name":"Perring Parkway", "lat":39.364668, "lng":-76.573495,
     "aliases":["perring parkway"], "videos":[]},
    {"name":"Spelman Rd (Cherry Hill)", "lat":39.246184, "lng":-76.628485,
     "aliases":["spelman rd"], "videos":[]},
    {"name":"Turner Station (Dundalk)", "lat":39.244863, "lng":-76.508672,
     "aliases":["turner station"], "videos":[]},
    {"name":"Westchester Ave near Frederick Rd", "lat":39.268097, "lng":-76.792403,
     "aliases":["westchester avenue near frederick road"], "videos":[]},
    {"name":"US-29 Colesville Rd (Montgomery Co.)", "lat":39.0700, "lng":-77.0300,
     "aliases":["us-29colesville road in montgomery county, md"], "videos":[]},
    {"name":"Joppatowne, Harford County", "lat": 39.413915, "lng":-76.356395,
     "aliases":["joppatowne, harford county"], "videos":[]},
    {"name":"Doncaster Rd, Joppatowne", "lat":39.415303, "lng":-76.36641,
     "aliases":["doncaster rd, joppatowne"], "videos":[]},
    {"name":"Broadway St East (Richford–Vinal)", "lat":39.3050, "lng":-76.5900,
     "aliases":["broadway street east between richford and vinal streets",
                "east broadway street between richford and vinal streets"], "videos":[]},
    {"name":"White Marsh, Baltimore County", "lat":39.383655, "lng":-76.451127,
     "aliases":["white marsh, baltimore county"], "videos":[]},
    {"name":"Sawmill Creek", "lat":39.181561, "lng":-76.619015,
     "aliases":["sawmill creek"], "videos":[]},
    {"name":"Silver Spring (NE Baltimore)", "lat":39.39063, "lng":-76.488854,
     "aliases":["silver spring"], "videos":[]},
    {"name":"Spring Valley", "lat":39.413817, "lng":-76.644903,
     "aliases":["spring valley"], "videos":[]},
]

ALIAS = {}
for gi, g in enumerate(GROUPS):
    for a in g["aliases"]:
        ALIAS[a] = gi

def norm_base(fn):
    base = os.path.splitext(fn)[0]
    base = re.sub(r"_\d+$", "", base)          # strip trailing _N
    base = base.replace("_", " ")
    base = re.sub(r"\s+", " ", base).strip()
    base = base.rstrip(".").strip()
    return base.lower()

def sort_key(fn):
    base = os.path.splitext(fn)[0]
    m = re.search(r"_(\d+)$", base)
    return (1, int(m.group(1))) if m else (0, 0)

# ---- scan the folder ----
files = [f for f in os.listdir(IMGDIR)
         if os.path.isfile(os.path.join(IMGDIR, f))
         and f.lower().split(".")[-1] in ("jpg","jpeg","png","gif","webp")]

group_imgs = {}
skipped = []
for f in sorted(files):
    if re.match(r"^s\d{2}_\d", f):             # leftover PPTX slide exports (no location) -> skip
        skipped.append(f); continue
    key = norm_base(f)
    if key not in ALIAS:
        skipped.append(f); continue
    group_imgs.setdefault(ALIAS[key], []).append(f)

FLOOD_REPORTS = []
for gi, g in enumerate(GROUPS):
    imgs = group_imgs.get(gi)
    if not imgs:
        continue
    imgs = sorted(imgs, key=sort_key)
    FLOOD_REPORTS.append({
        "name": g["name"], "lat": g["lat"], "lng": g["lng"],
        "source": "Reported flooding (validated photos)",
        "images": ["images/reports/" + f for f in imgs],
        "videos": g["videos"],
    })

print("FLOOD groups with photos:", len(FLOOD_REPORTS))
for r in FLOOD_REPORTS:
    print("  %-42s %2d imgs %s" % (r["name"][:42], len(r["images"]), "[video]" if r["videos"] else ""))
if skipped:
    print("skipped (no location match / slide exports):", len(skipped))

# ---------------------------------------------------------------------------
# 3) ROAD CLOSURES (separate layer) — hardcoded coords, de-duplicated
# ---------------------------------------------------------------------------
ROADCLOSURE_REPORTS = [
    {"name":"Aliceanna St (Caroline–Bond)",              "lat":39.28300, "lng":-76.59450},
    {"name":"Caroline St (Thames–Aliceanna)",            "lat":39.28280, "lng":-76.59650},
    {"name":"Hillen Rd at 35th St",                       "lat":39.330976,"lng":-76.590586},
    {"name":"Mount Washington at 5910 Falls Rd",          "lat":39.369478,"lng":-76.649154},
    {"name":"Meadow Mill at 3600 Clipper Mill Rd",        "lat":39.330891,"lng":-76.642464},
    {"name":"Purnell Dr at W. Forest Park Ave",           "lat":39.318742,"lng":-76.703573},
    {"name":"600 block of W. Patapsco Ave",               "lat":39.241909,"lng":-76.626319},
    {"name":"South Hanover St",                           "lat":39.256607,"lng":-76.616793},
    {"name":"Frankfurst Ave",                             "lat":39.241489,"lng":-76.592085},
    {"name":"Frederick Ave at North Bend Rd",             "lat":39.280808,"lng":-76.705505},
    {"name":"Frederick Ave at Beechfield Ave",            "lat":39.281434,"lng":-76.693657},
    {"name":"North Point Rd at Quad Ave",                 "lat":39.300137,"lng":-76.535470},
    {"name":"East Monument St at Pulaski Hwy",            "lat":39.299865,"lng":-76.554400},
    {"name":"Fleet St at Aliceanna St",                   "lat":39.284503,"lng":-76.594386},
    {"name":"Fleet St at Caroline St",                    "lat":39.284342,"lng":-76.596722},
    {"name":"Mallow Hill Rd",                             "lat":39.281902,"lng":-76.710575},
    {"name":"Smith Avenue Bridge",                        "lat":39.371338,"lng":-76.637182},
    {"name":"S. Beechfield Ave",                          "lat":39.273093,"lng":-76.693143},
    {"name":"North Bend Rd",                              "lat":39.285527,"lng":-76.710465},
    {"name":"Purnell Dr",                                 "lat":39.320275,"lng":-76.708194},
    {"name":"Reedbird Ave",                               "lat":39.248614,"lng":-76.616377},
    {"name":"East Patapsco Ave at Shell Rd",              "lat":39.232379,"lng":-76.584993},
    {"name":"North Point Rd at Kane St",                  "lat":39.296907,"lng":-76.529646},
    {"name":"West Patapsco Ave",                          "lat":39.239499,"lng":-76.612345},
    {"name":"Thames St at Central Ave",                   "lat":39.28180, "lng":-76.59750},
    {"name":"Frankfurst Ave at Potee St",                "lat":39.242911,"lng":-76.608843},
    {"name":"North Franklintown Rd near Leon Day Park",  "lat":39.299835,"lng":-76.670521},
    {"name":"Kelly Avenue Bridge",                        "lat":39.366711,"lng":-76.651821},
    {"name":"Monument St at Haven St",                    "lat":39.299560,"lng":-76.563449},
    {"name":"700 block of Wolf St",                       "lat":39.298406,"lng":-76.590989},
    {"name":"Eastern Ave (Greektown–Highlandtown)",      "lat":39.28700, "lng":-76.56700},
]
# de-duplicate by rounded coordinate
seen = set(); RCL = []
for r in ROADCLOSURE_REPORTS:
    k = (round(r["lat"], 4), round(r["lng"], 4))
    if k in seen: continue
    seen.add(k)
    r["source"] = "Known City flood-related road closure"
    RCL.append(r)
ROADCLOSURE_REPORTS = RCL
print("ROAD CLOSURES:", len(ROADCLOSURE_REPORTS))

# ---------------------------------------------------------------------------
# 4) Read existing SOCIAL / YOUTUBE / MYCOAST from reports.js
# ---------------------------------------------------------------------------
txt = io.open(REPORTS_JS, encoding="utf-8").read()
def extract(name):
    m = re.search(r"const\s+" + name + r"\s*=\s*(\[.*?\]);", txt, re.S)
    return json.loads(m.group(1)) if m else []

SOCIAL_REPORTS  = extract("SOCIAL_REPORTS")
YOUTUBE_REPORTS = extract("YOUTUBE_REPORTS")
MYCOAST_REPORTS = extract("MYCOAST_REPORTS")

# NEW social/newsletter lines that were NOT already present
NEW_SOCIAL = [
    {"name":"E Belvedere Ave & York Rd (21212)", "lat":39.3663, "lng":-76.6102},
    {"name":"Washington St & Lanvale",           "lat":39.3095, "lng":-76.5905},
    {"name":"2400 block of Biddle Street",       "lat":39.3080, "lng":-76.5880},
    {"name":"1900 block E Preston St",           "lat":39.3058, "lng":-76.5928},
    {"name":"E Biddle St & N Milton Ave",        "lat":39.3068, "lng":-76.5822},
    {"name":"Russell St & Hamburg St",           "lat":39.2795, "lng":-76.6262},
]
have = set(r["name"].strip().lower() for r in SOCIAL_REPORTS)
added = 0
for r in NEW_SOCIAL:
    if r["name"].strip().lower() in have:
        continue
    r["source"] = "Social media & newsletter flooded-street report"
    r["videos"] = []
    SOCIAL_REPORTS.append(r); added += 1
print("SOCIAL total:", len(SOCIAL_REPORTS), "(added", added, "new)")

# Remove the out-of-area beach / tidal MyCoast point (not Baltimore)
before = len(MYCOAST_REPORTS)
MYCOAST_REPORTS = [m for m in MYCOAST_REPORTS
                   if not (abs(m["lat"]-39.18421) < 0.002 and abs(m["lng"]+76.55373) < 0.002)
                   and m["lat"] >= 39.19]     # drop anything south of the Beltway (tidal/beach)
print("MYCOAST:", len(MYCOAST_REPORTS), "(removed", before-len(MYCOAST_REPORTS), "beach/tidal)")

# ---------------------------------------------------------------------------
# 5) Write reports.js
# ---------------------------------------------------------------------------
def dump(name, arr):
    return "const " + name + "=" + json.dumps(arr, ensure_ascii=False) + ";\n"

with io.open(REPORTS_JS, "w", encoding="utf-8") as f:
    f.write("// FloodLens reported-flooding data. Rebuilt offline by _rebuild_all.py.\n")
    f.write("// FLOOD_REPORTS = validated photos scanned from images/reports/ (grouped by location).\n")
    f.write(dump("FLOOD_REPORTS", FLOOD_REPORTS))
    f.write(dump("SOCIAL_REPORTS", SOCIAL_REPORTS))
    f.write(dump("YOUTUBE_REPORTS", YOUTUBE_REPORTS))
    f.write(dump("MYCOAST_REPORTS", MYCOAST_REPORTS))
    f.write(dump("ROADCLOSURE_REPORTS", ROADCLOSURE_REPORTS))
    f.write("const NEWS_REPORTS=[];\n")   # News layer retired -> folded into Social
print("wrote", REPORTS_JS)
