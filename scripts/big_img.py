#!/usr/bin/env python3
"""Fetch BIG CTSRT imagery grid. usage: big_img.py SERVICE minx miny maxx maxy step outdir [px_per_deg]"""
import sys, os, requests, time
S,minx,miny,maxx,maxy,step,out=sys.argv[1],*map(float,sys.argv[2:7]),sys.argv[7]
ppd=float(sys.argv[8]) if len(sys.argv)>8 else 100000  # ~1.1 m/px
U=f"https://geoservices.big.go.id/raster/rest/services/IMAGERY/{S}/ImageServer/exportImage"
os.makedirs(out,exist_ok=True)
y=maxy; r=0
while y>miny+1e-9:
    x=minx; c=0
    while x<maxx-1e-9:
        fn=f"{out}/r{r:02d}_c{c:02d}_{y:.3f}_{x:.3f}.jpg"
        if not os.path.exists(fn):
            n=int(step*ppd)
            for t in range(3):
                try:
                    rr=requests.get(U,params=dict(bbox=f"{x},{y-step},{x+step},{y}",bboxSR=4326,imageSR=4326,size=f"{n},{n}",format="jpg",compressionQuality=85,f="image"),timeout=180)
                    if rr.ok and rr.content[:2]==b'\xff\xd8': open(fn,"wb").write(rr.content); break
                except Exception as e: print(e)
                time.sleep(3)
        x+=step; c+=1
    y-=step; r+=1
print("done")
