#!/usr/bin/env python3
"""DEMNAS (BIG public ImageServer) fetch + visualization.
usage: demnas_viz.py fetch name minx miny maxx maxy   -> data/demnas/name.tif
       demnas_viz.py viz in.tif out_prefix [sigma_px]  -> hillshade + local relief PNG"""
import sys, os, numpy as np, requests, rasterio
from scipy import ndimage
from PIL import Image
URL="https://geoservices.big.go.id/raster/rest/services/DEMNAS/DEM_Indonesia/ImageServer/exportImage"
PX=7.4985003e-05
def fetch(name,minx,miny,maxx,maxy,out_dir="data/demnas"):
    os.makedirs(out_dir,exist_ok=True)
    w=int(round((maxx-minx)/PX)); h=int(round((maxy-miny)/PX))
    assert w<=15000 and h<=4100, (w,h)
    p=dict(bbox=f"{minx},{miny},{maxx},{maxy}",bboxSR=4326,imageSR=4326,size=f"{w},{h}",format="tiff",
           pixelType="F32",interpolation="RSP_NearestNeighbor",f="image")
    r=requests.get(URL,params=p,timeout=300); r.raise_for_status()
    fn=f"{out_dir}/{name}.tif"; open(fn,"wb").write(r.content); return fn
def load(fn):
    r=rasterio.open(fn); a=r.read(1).astype("float64")
    a[(a<-500)|(a>6000)]=np.nan
    return r,a
def hill(a,dx,dy,az=315,alt=45):
    gy,gx=np.gradient(a,dy,dx)
    slope=np.arctan(np.hypot(gx,gy)); aspect=np.arctan2(-gx,gy)
    azr=np.radians(az); altr=np.radians(alt)
    hs=np.sin(altr)*np.cos(slope)+np.cos(altr)*np.sin(slope)*np.cos(azr-aspect)
    return np.clip(hs,0,1)
def viz(fn,prefix,sigma=6):
    r,a=load(fn)
    lat=r.bounds.top/2+r.bounds.bottom/2
    dx=abs(r.transform.a)*111320*np.cos(np.radians(lat)); dy=abs(r.transform.e)*110574
    m=np.isnan(a); f=np.where(m,np.nanmean(a),a)
    hs=np.mean([hill(f,dx,dy,az) for az in (315,45,135,225,0)],axis=0)
    lrm=f-ndimage.gaussian_filter(f,sigma)
    lim=np.nanpercentile(np.abs(lrm),98)
    l=np.clip((lrm/lim+1)/2,0,1)
    rgb=np.dstack([l,l,l])*0.6+np.dstack([hs]*3)*0.4
    Image.fromarray((np.dstack([hs]*3)*255).astype("uint8")).save(prefix+"_hs.png")
    Image.fromarray((rgb*255).astype("uint8")).save(prefix+"_lrm.png")
    return dx,dy
if __name__=="__main__":
    if sys.argv[1]=="fetch": print(fetch(sys.argv[2],*map(float,sys.argv[3:7])))
    else: print(viz(sys.argv[2],sys.argv[3],float(sys.argv[4]) if len(sys.argv)>4 else 6))
