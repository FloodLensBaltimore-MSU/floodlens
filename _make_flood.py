# -*- coding: utf-8 -*-
"""
CityCAT max-depth rasters -> browser assets, all in EPSG:3857 (Leaflet's display
projection) so the overlay AND the depth lookups line up pixel-for-pixel with the
basemap and buildings.
  * hi-res transparent PNG per scenario (sharp when zoomed in)
  * coarser depth grid (cm ints, row-major north->south) per scenario for lookups
  * prefetch seeds (wettest points, normalized in the 3857 frame)
"""
import io, json
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling, transform_bounds
from PIL import Image

BASE = r"E:\CityCAT Analysis\CityCAT_2026\GCP_files\Beltway_10m DEM\Beltway_Postprocessed_SEAMFREE_Beltway"
OUTDIR = r"e:\CityCAT Analysis\CityCAT_2026\Flood Risk Tool_New"
SCEN = {
    "10_1":  "Beltway_10yr_1hr_MaxDepth_SEAMFREE.tif",
    "10_24": "Beltway_10yr_24hr_MaxDepth_SEAMFREE.tif",
    "100_1": "Beltway_100yr_1hr_MaxDepth_SEAMFREE.tif",
    "100_24":"Beltway_100yr_24hr_MaxDepth_SEAMFREE.tif",
}

# lat/lng frame -> its EPSG:3857 bbox (square-ish pixels there)
W,Sd,E,N = -76.905, 39.106, -76.274, 39.510
minx,miny,maxx,maxy = transform_bounds("EPSG:4326","EPSG:3857",W,Sd,E,N)
# imageOverlay bounds = lat/lng of the 3857 rectangle corners (so Leaflet aligns it)
south,west,north,east = transform_bounds("EPSG:3857","EPSG:4326",minx,miny,maxx,maxy)[1], \
                        transform_bounds("EPSG:3857","EPSG:4326",minx,miny,maxx,maxy)[0], \
                        transform_bounds("EPSG:3857","EPSG:4326",minx,miny,maxx,maxy)[3], \
                        transform_bounds("EPSG:3857","EPSG:4326",minx,miny,maxx,maxy)[2]

PW = 2200                                   # PNG width (sharp)
PH = int(round(PW*(maxy-miny)/(maxx-minx)))
GW = 1400                                   # depth-grid width (lookup)
GH = int(round(GW*(maxy-miny)/(maxx-minx)))
print("png",PW,"x",PH," grid",GW,"x",GH)

shallow=np.array([198,219,239]); mid=np.array([66,146,198]); deep=np.array([8,48,107])
def ramp(d):
    t=np.clip((d-0.10)/1.90,0,1); tp=t**0.85
    lo=tp<0.5
    c=np.empty(d.shape+(3,),dtype=np.float32)
    f=(tp/0.5)[...,None]
    c[lo]=(shallow+(mid-shallow)*f)[lo]
    f2=((tp-0.5)/0.5)[...,None]
    c[~lo]=(mid+(deep-mid)*f2)[~lo]
    a=np.clip(255*(0.55+0.45*t),0,255)
    return c,a

def warp(ds, w, h):
    dst=np.full((h,w),np.nan,dtype=np.float32)
    reproject(source=rasterio.band(ds,1), destination=dst,
        src_transform=ds.transform, src_crs=ds.crs,
        dst_transform=rasterio.transform.from_bounds(minx,miny,maxx,maxy,w,h),
        dst_crs="EPSG:3857", src_nodata=ds.nodata, dst_nodata=np.nan,
        resampling=Resampling.bilinear)
    d=dst; d[~np.isfinite(d)]=0.0; d[d<0]=0.0; d[d>10]=10.0
    return d

FLOOD_IMG={}; FLOOD_DEPTH={}
for key,fn in SCEN.items():
    ds=rasterio.open(BASE+"\\"+fn)
    # PNG (hi-res)
    dp=warp(ds,PW,PH); wetp=dp>=0.10
    rgba=np.zeros((PH,PW,4),dtype=np.uint8); c,a=ramp(dp)
    rgba[...,0]=c[...,0]; rgba[...,1]=c[...,1]; rgba[...,2]=c[...,2]
    rgba[...,3]=np.where(wetp,a,0).astype(np.uint8)
    imgname="images/flood_%s.png"%key
    Image.fromarray(rgba,"RGBA").save(OUTDIR+"\\"+imgname.replace("/","\\"))
    FLOOD_IMG[key]=imgname
    # depth grid (lookup)
    dg=warp(ds,GW,GH); cm=np.where(dg>=0.10,np.round(dg*100),0).astype(np.int32)
    FLOOD_DEPTH[key]=cm.flatten().tolist()
    print(key,"wet",int((dg>=0.10).sum()),"maxcm",int(cm.max()))

ref=np.array(FLOOD_DEPTH["100_24"]).reshape(GH,GW)
seeds=[]; NB=6
for by in range(NB):
    for bx in range(NB):
        y0=by*GH//NB; y1=(by+1)*GH//NB; x0=bx*GW//NB; x1=(bx+1)*GW//NB
        sub=ref[y0:y1,x0:x1]
        if sub.size==0 or sub.max()<30: continue
        iy,ix=np.unravel_index(sub.argmax(),sub.shape)
        seeds.append([round((x0+ix)/(GW-1),4), round((y0+iy)/(GH-1),4), 1.0])
print("seeds",len(seeds))

with io.open(OUTDIR+r"\data\flood.js","w",encoding="utf-8") as f:
    f.write("// Real CityCAT max-depth flood model (Beltway, SEAMFREE), EPSG:3857 aligned.\n")
    f.write("// Depth grids: cm int, row-major north->south, GW x GH; 0 = dry.\n")
    f.write("const FLOOD_BOUNDS=%s;\n"%json.dumps([[south,west],[north,east]]))
    f.write("const FLOOD_MERC=%s;\n"%json.dumps([minx,miny,maxx,maxy]))
    f.write("const FLOOD_GW=%d, FLOOD_GH=%d;\n"%(GW,GH))
    f.write("const FLOOD_IMG=%s;\n"%json.dumps(FLOOD_IMG))
    f.write("const FLOOD_SEEDS=%s;\n"%json.dumps(seeds))
    f.write("const FLOOD_DEPTH=%s;\n"%json.dumps(FLOOD_DEPTH))
print("wrote data/flood.js")
