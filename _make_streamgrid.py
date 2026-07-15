# -*- coding: utf-8 -*-
"""
Crop the statewide StreamStats stream grid (streamgrid.tif, EPSG:5070, 0/1 mask)
to the Baltimore Beltway study area, reproject to Web Mercator (EPSG:3857 — the
Leaflet display projection, so the overlay lines up exactly), and write a
transparent PNG (blue where stream cells = 1). Also emit the lat/lng bounds so
the app can drop it in as an L.imageOverlay with no server required.
"""
import io, json, math
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio.windows import from_bounds
from PIL import Image

SRC = r"E:\Data\md_streamStats\md_streamStats\streamgrid.tif"
OUT_PNG = r"e:\CityCAT Analysis\CityCAT_2026\Flood Risk Tool_New\images\streamgrid.png"
OUT_JS  = r"e:\CityCAT Analysis\CityCAT_2026\Flood Risk Tool_New\data\streamgrid.js"

# Beltway study-area bbox in lat/lng (a touch wider than beltwayBounds)
W,Sm,E,N = -76.83, 39.15, -76.27, 39.52

ds = rasterio.open(SRC)

# window bounds in the source CRS (5070)
l,b,r,t = transform_bounds("EPSG:4326", ds.crs, W, Sm, E, N, densify_pts=21)
win = from_bounds(l,b,r,t, transform=ds.transform)
src_arr = ds.read(1, window=win)
src_transform = ds.window_transform(win)
print("cropped window shape:", src_arr.shape)

# destination grid in EPSG:3857 covering the same bbox
dst_crs = "EPSG:3857"
x0,y0,x1,y1 = transform_bounds("EPSG:4326", dst_crs, W, Sm, E, N)
# target pixel size ~ keep width around 2400 px
DST_W = 2400
DST_H = int(round(DST_W * (y1-y0)/(x1-x0)))
dst_transform = rasterio.transform.from_bounds(x0,y0,x1,y1, DST_W, DST_H)
dst = np.zeros((DST_H, DST_W), dtype=np.uint8)

reproject(
    source=src_arr, destination=dst,
    src_transform=src_transform, src_crs=ds.crs,
    dst_transform=dst_transform, dst_crs=dst_crs,
    resampling=Resampling.max)  # keep thin stream cells (max preserves 1s)

# build RGBA: stream cells -> solid blue, else transparent
rgba = np.zeros((DST_H, DST_W, 4), dtype=np.uint8)
mask = dst > 0
rgba[...,0][mask] = 42    # #2a7fbf
rgba[...,1][mask] = 127
rgba[...,2][mask] = 191
rgba[...,3][mask] = 235
Image.fromarray(rgba, "RGBA").save(OUT_PNG)
print("wrote", OUT_PNG, DST_W, "x", DST_H, "stream px:", int(mask.sum()))

# imageOverlay bounds must be the lat/lng of the 3857 bbox corners so Leaflet
# (which works in 3857) places the image exactly.
sw = transform_bounds(dst_crs, "EPSG:4326", x0,y0,x0,y0)[:2]  # (lng,lat) of SW
ne = transform_bounds(dst_crs, "EPSG:4326", x1,y1,x1,y1)[:2]
# transform_bounds returns (w,s,e,n); for a point w==e,s==n
swb = transform_bounds(dst_crs, "EPSG:4326", x0,y0,x1,y1)
south,west,north,east = swb[1],swb[0],swb[3],swb[2]
bounds = [[south,west],[north,east]]
with io.open(OUT_JS,"w",encoding="utf-8") as f:
    f.write("// StreamStats stream grid (USGS), cropped to the Beltway, EPSG:3857 PNG overlay.\n")
    f.write("const STREAMGRID_IMG=\"images/streamgrid.png\";\n")
    f.write("const STREAMGRID_BOUNDS=" + json.dumps(bounds) + ";\n")
print("wrote", OUT_JS, "bounds", bounds)
