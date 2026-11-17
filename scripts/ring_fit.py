"""ring_fit.py file.laz epsg lat lon : azimuthal analysis of a ring ditch around a summit (ground TIN 0.5 m)"""
import sys, numpy as np, laspy
from pyproj import Transformer
from scipy.interpolate import griddata
f,epsg,lat,lon=sys.argv[1],int(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]); H=80
cx,cy=Transformer.from_crs(4326,epsg,always_xy=True).transform(lon,lat)
X=[];Y=[];Z=[]
with laspy.open(f) as r:
    for p in r.chunk_iterator(2_000_000):
        c=np.asarray(p.classification)==2; x,y=np.asarray(p.x),np.asarray(p.y); m=c&(abs(x-cx)<H)&(abs(y-cy)<H)
        if m.any(): X.append(x[m]-cx);Y.append(y[m]-cy);Z.append(np.asarray(p.z)[m])
X,Y,Z=map(np.concatenate,(X,Y,Z))
s=0.5; gx,gy=np.meshgrid(np.arange(-H,H,s),np.arange(-H,H,s)); zg=griddata((X,Y),Z,(gx,gy),'linear')
# centroid of >32.3 m area as centre
m=(zg>np.nanmax(zg[np.hypot(gx,gy)<20])-0.6)&(np.hypot(gx,gy)<25); ox,oy=gx[m].mean(),gy[m].mean(); print(f'centre offset {ox:.1f},{oy:.1f} m')
rs=np.arange(0,60,0.5); res=[]
for az in range(0,360,15):
    t=np.radians(az); px=ox+rs*np.sin(t); py=oy+rs*np.cos(t)
    ii=((py+H)/s).astype(int); jj=((px+H)/s).astype(int); z=zg[ii,jj]
    k=np.nanargmin(np.where((rs>15)&(rs<50),z,np.nan)); top=np.nanmean(z[rs<8])
    outer=np.nanmax(z[k:min(len(z),k+30)]) if k+2<len(z) else np.nan
    # inner edge: first r where z drops 0.3 below top
    e=np.argmax(z<top-0.3) if (z<top-0.3).any() else -1
    res.append((az,rs[k],z[k],top-z[k],outer-z[k],rs[e]))
    print(f'az {az:3d}: ditch r={rs[k]:4.1f} m z={z[k]:.2f} depth below top {top-z[k]:.2f} below outer max(15m) {outer-z[k]:.2f}; interior edge r={rs[e]:.1f}')
a=np.array(res); print(f'ditch radius mean {a[:,1].mean():.1f} sd {a[:,1].std():.1f}; interior-edge radius mean {a[:,5].mean():.1f} sd {a[:,5].std():.1f}; top-ditch {a[:,3].mean():.2f}; outer-ditch {a[:,4].mean():.2f} (min {a[:,4].min():.2f})')
