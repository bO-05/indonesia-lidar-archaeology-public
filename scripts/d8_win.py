"""Render hillshade + LRM window: d8_win.py tile lat lon half_km out.png [lrm_px=25]"""
import sys,numpy as np; sys.path.insert(0,'scripts'); from d8_relief import *
from scipy import ndimage; from PIL import Image, ImageDraw
t,lat,lon,hk,out=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),sys.argv[5]
k=int(sys.argv[6]) if len(sys.argv)>6 else 25
r,a,dx,dy=load(f'data/demnas8/DEMNAS_{t}_v1.0.tif'); row,col=r.index(lon,lat); h=int(hk*1000/dx)
r0,c0=max(0,row-h),max(0,col-h); w=a[r0:row+h,c0:col+h]
f=fill(w); hs=hill(f*float(__import__("os").environ.get("VE","1")),dx,dy); g=ndimage.gaussian_filter(f,1); l=g-ndimage.median_filter(g,size=k)
def im(x,lo,hi): return Image.fromarray(np.clip((x-lo)/(hi-lo)*255,0,255).astype('uint8')).convert('RGB')
lo,hi=np.percentile(f,[2,98])
ims=[im(hs,0,1),im(l,-2.5,2.5),im(f,lo,hi)]
S=700; ims=[i.resize((S,S)) for i in ims]; c=Image.new('RGB',(3*S+20,S+20),'white')
for i,x in enumerate(ims):
    d=ImageDraw.Draw(x); px=(col-c0)/w.shape[1]*S; py=(row-r0)/w.shape[0]*S; d.ellipse([px-6,py-6,px+6,py+6],outline=(255,0,0),width=2)
    sb=1000/dx/w.shape[1]*S; d.line([10,S-15,10+sb,S-15],fill=(255,255,0),width=3); d.text((12,S-30),'1 km',fill=(255,255,0))
    c.paste(x,(i*(S+10),10))
ImageDraw.Draw(c).text((5,0),f'{t} hillshade | LRM {k*8}m +-2.5m | elev {lo:.0f}-{hi:.0f}m',fill=(0,0,0)); c.save(out); print(out)
