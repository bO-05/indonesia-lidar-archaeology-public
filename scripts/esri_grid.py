#!/usr/bin/env python3
"""Esri World Imagery mosaic for bbox. usage: esri_grid.py minlon minlat maxlon maxlat zoom out.jpg
Writes out.jpg + out.json (tile origin) ; px->latlon via px2ll(out.json,x,y)."""
import sys, math, io, json, requests, concurrent.futures as cf
from PIL import Image
def t(lon,lat,z):
    N=2**z; return (lon+180)/360*N, (1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*N
def px2ll(meta,x,y):
    z=meta['z']; N=2**z; fx=meta['x0']+x/256; fy=meta['y0']+y/256
    return math.degrees(math.atan(math.sinh(math.pi*(1-2*fy/N)))), fx/N*360-180
def fetch(minlon,minlat,maxlon,maxlat,z,out,src='esri'):
    x0,y0=map(int,t(minlon,maxlat,z)); x1,y1=map(int,t(maxlon,minlat,z))
    W,H=x1-x0+1,y1-y0+1; img=Image.new('RGB',(256*W,256*H))
    s=requests.Session(); s.headers['User-Agent']='Mozilla/5.0'
    def g(ij):
        i,j=ij; u=f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y0+j}/{x0+i}'
        for _ in range(3):
            try:
                r=s.get(u,timeout=30)
                if r.ok: return i,j,Image.open(io.BytesIO(r.content)).convert('RGB')
            except Exception: pass
        return i,j,None
    with cf.ThreadPoolExecutor(16) as ex:
        for i,j,im in ex.map(g,[(i,j) for i in range(W) for j in range(H)]):
            if im: img.paste(im,(256*i,256*j))
    img.save(out,quality=88); m=dict(z=z,x0=x0,y0=y0,W=W*256,H=H*256)
    json.dump(m,open(out.rsplit('.',1)[0]+'.json','w')); return m
if __name__=='__main__':
    a=sys.argv; print(fetch(*map(float,a[1:5]),int(a[5]),a[6]))
