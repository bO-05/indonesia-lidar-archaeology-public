#!/usr/bin/env python3
"""DEMNAS-16m isolated-peak detector + Esri chips. usage: bj_peaks.py name minx miny maxx maxy outdir"""
import sys, os, json, math, numpy as np, rasterio
sys.path.insert(0,os.path.dirname(__file__)); import demnas_viz as d, esri_grid as eg
from scipy import ndimage
from PIL import Image, ImageDraw
name,minx,miny,maxx,maxy,out=sys.argv[1],*map(float,sys.argv[2:6]),sys.argv[6]
os.makedirs(out,exist_ok=True); d.PX=0.000152
fn=f"data/demnas/{name}_16m.tif"
if not os.path.exists(fn): d.fetch(name+'_16m',minx,miny,maxx,maxy)
r=rasterio.open(fn); a=r.read(1).astype(float); a[np.abs(a)>1e6]=np.nan; a=np.where(np.isnan(a),np.nanmedian(a),a)
bg=ndimage.median_filter(a,size=21); rel=a-bg
mx=ndimage.maximum_filter(rel,size=9)
pk=np.argwhere((rel==mx)&(rel>2.0)&(rel<12))
# isolation: peak footprint small -> fraction of 9x9 window >1 m must be <0.35 (excludes villages/tree belts)
cands=[]
for y,x in pk:
    w=rel[max(0,y-4):y+5,max(0,x-4):x+5]; frac=(w>1.0).mean()
    if frac<0.35:
        lon,lat=r.xy(y,x); cands.append(dict(lat=lat,lon=lon,rel=float(rel[y,x]),frac=float(frac)))
cands.sort(key=lambda c:-c['rel']); print(len(pk),'peaks',len(cands),'isolated')
json.dump(cands,open(f"{out}/peaks.json","w"),indent=1)
chips=[]
for i,c in enumerate(cands[:int(sys.argv[7]) if len(sys.argv)>7 else 48]):
    f=f"{out}/chip_{i:03d}.jpg"; h=0.0012
    if not os.path.exists(f): eg.fetch(c['lon']-h,c['lat']-h,c['lon']+h,c['lat']+h,18,f)
    im=Image.open(f); m=json.load(open(f[:-4]+'.json'))
    N=2**18; fx=(c['lon']+180)/360*N; fy=(1-math.asinh(math.tan(math.radians(c['lat'])))/math.pi)/2*N
    px,py=(fx-m['x0'])*256,(fy-m['y0'])*256; S=256
    im=im.crop((int(px-S),int(py-S),int(px+S),int(py+S))).resize((256,256)); dr=ImageDraw.Draw(im)
    dr.ellipse([118,118,138,138],outline=(255,255,0)); dr.text((3,3),f"{i} +{c['rel']:.1f}m",fill=(255,255,0)); chips.append(im)
for k in range(0,len(chips),16):
    M=Image.new('RGB',(1024,1024))
    for j,im in enumerate(chips[k:k+16]): M.paste(im,((j%4)*256,(j//4)*256))
    M.save(f"{out}/sheet_{k//16:02d}.jpg",quality=90)
