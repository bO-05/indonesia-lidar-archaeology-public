#!/usr/bin/env python3
"""DEMNAS 8 m relief tools. import: load(tile) -> (r,a,dx,dy); rel(a,size); sample(r,rel,lat,lon,rad)"""
import numpy as np, rasterio
from scipy import ndimage
def load(fn):
    r=rasterio.open(fn); a=r.read(1).astype('float64'); a[~np.isfinite(a)|(a<-100)]=np.nan
    lat=(r.bounds.top+r.bounds.bottom)/2; dx=abs(r.res[0])*111320*np.cos(np.radians(lat)); dy=abs(r.res[1])*110574
    return r,a,dx,dy
def fill(a): return np.where(np.isnan(a),np.nanmedian(a),a)
def rel_median(a,size): f=fill(a); return f-ndimage.median_filter(f,size=size)
def tpi(a,rad):
    f=fill(a); y,x=np.ogrid[-rad:rad+1,-rad:rad+1]; k=((x*x+y*y)<=rad*rad)&((x*x+y*y)>(rad//2)**2); k=k/k.sum()
    return f-ndimage.convolve(f,k)
def hill(a,dx,dy,az=315,alt=45):
    f=fill(a); gy,gx=np.gradient(f,dy,dx); sl=np.arctan(np.hypot(gx,gy)); asp=np.arctan2(-gx,gy)
    return np.clip(np.sin(np.radians(alt))*np.cos(sl)+np.cos(np.radians(alt))*np.sin(sl)*np.cos(np.radians(az)-asp),0,1)
def sample(r,rel,lat,lon,rad=3):
    row,col=r.index(lon,lat); w=rel[max(0,row-rad):row+rad+1,max(0,col-rad):col+rad+1]; return float(np.nanmax(w))
