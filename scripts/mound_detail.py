"""Close-up of a small mound from ground points: 0.25 m TIN hillshade + 0.25 m contours, radial mean profile around
the local summit, and fitted dimensions. Usage: mound_detail.py file.laz epsg lat lon half_m out.png"""
import sys, numpy as np, laspy
from pyproj import Transformer
from scipy.interpolate import griddata
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f,epsg,lat,lon,H,out=sys.argv[1],int(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]),sys.argv[6]
cx,cy=Transformer.from_crs(4326,epsg,always_xy=True).transform(lon,lat)
X=[];Y=[];Z=[]
with laspy.open(f) as r:
    for p in r.chunk_iterator(2_000_000):
        c=np.asarray(p.classification)==2; x,y=np.asarray(p.x),np.asarray(p.y); m=c&(abs(x-cx)<H+5)&(abs(y-cy)<H+5)
        if m.any(): X.append(x[m]-cx);Y.append(y[m]-cy);Z.append(np.asarray(p.z)[m])
X,Y,Z=map(np.concatenate,(X,Y,Z))
s=0.25; gx,gy=np.meshgrid(np.arange(-H,H,s),np.arange(-H,H,s)); zg=griddata((X,Y),Z,(gx,gy),'linear')
c=np.nanargmax(np.where(np.hypot(gx,gy)<15,zg,-np.inf)); sx,sy=gx.flat[c],gy.flat[c]
base=np.nanpercentile(zg,20); print(f'summit offset ({sx:.1f},{sy:.1f}) m, summit z {zg.flat[c]:.2f}, base (p20) {base:.2f}, height {zg.flat[c]-base:.2f} m')
r=np.hypot(gx-sx,gy-sy); b=np.arange(0,H,1); prof=[np.nanmean(zg[(r>=b[i])&(r<b[i+1])]) for i in range(len(b)-1)]
print('radial mean z (1 m bins):',np.round(prof,2).tolist())
m=(zg-base)>0.3; lab=m&(r<30); 
if lab.any():
    yy=gy[lab]; xx=gx[lab]; print(f'>0.3 m above base footprint: x {xx.min():.1f}..{xx.max():.1f}, y {yy.min():.1f}..{yy.max():.1f}, area {lab.sum()*s*s:.0f} m2')
dy,dx=np.gradient(np.where(np.isfinite(zg),zg,base),s); hs=np.clip(0.5+(-dx+dy)*0.6,0,1)
fig,ax=plt.subplots(1,3,figsize=(20,6.5)); E=[-H,H,-H,H]
ax[0].imshow(hs,origin='lower',extent=E,cmap='gray'); ax[0].contour(gx,gy,zg,levels=np.arange(np.floor(np.nanmin(zg)),np.nanmax(zg),0.25),colors='y',linewidths=0.4); ax[0].plot(sx,sy,'r+'); ax[0].set_title('ground TIN 0.25 m, contours 0.25 m')
ax[1].scatter(X,Y,c=Z,s=2,cmap='terrain'); ax[1].set_aspect('equal'); ax[1].set_xlim(-H,H); ax[1].set_ylim(-H,H); ax[1].set_title(f'ground points ({len(X)}), colour z')
ax[2].plot(b[:-1]+0.5,prof,'k.-'); ax[2].grid(); ax[2].set_xlabel('m from summit'); ax[2].set_title('radial mean ground z')
plt.tight_layout(); plt.savefig(out,dpi=65); print(out)
