"""Full point-cloud check of a lead from a 1518 LAZ: ground TIN hillshade + LRM + ground z + canopy, ground-density
stats (centre vs annulus), 4 profiles through the centre (ground TIN and raw ground/non-ground points).
Usage: lead_pc.py file.laz epsg lat lon half_m out_prefix [vmin vmax]"""
import sys, numpy as np, laspy
from pyproj import Transformer
from scipy.interpolate import griddata
from scipy import ndimage, stats
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f, epsg, lat, lon, H, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
cx, cy = Transformer.from_crs(4326, epsg, always_xy=True).transform(lon, lat)
X=[];Y=[];Z=[];C=[]
with laspy.open(f) as r:
    h=r.header; print('bounds', h.mins[:2], h.maxs[:2], 'inside', h.mins[0]<=cx<=h.maxs[0] and h.mins[1]<=cy<=h.maxs[1])
    for p in r.chunk_iterator(2_000_000):
        x,y=np.asarray(p.x),np.asarray(p.y); m=(abs(x-cx)<H+20)&(abs(y-cy)<H+20)
        if m.any(): X.append(x[m]);Y.append(y[m]);Z.append(np.asarray(p.z)[m]);C.append(np.asarray(p.classification)[m])
X,Y,Z,C=map(np.concatenate,(X,Y,Z,C)); X-=cx; Y-=cy; g=C==2
print('points', len(X), 'classes', {int(k):int(v) for k,v in zip(*np.unique(C,return_counts=True))})
rr=np.hypot(X,Y)
for a,b in ((0,15),(0,30),(30,60),(60,120)):
    m=(rr>=a)&(rr<b); ar=np.pi*(b*b-a*a)
    print(f'ring {a}-{b} m: ground {(m&g).sum()/ar:.3f}/m2, all {m.sum()/ar:.2f}/m2, ground z med {np.median(Z[m&g]) if (m&g).any() else np.nan:.2f}, p90 all-return height above ground med {np.percentile(Z[m],90)-np.median(Z[m&g]) if (m&g).any() else np.nan:.1f}')
gx,gy=np.meshgrid(np.arange(-H,H,0.5),np.arange(-H,H,0.5))
zg=griddata((X[g],Y[g]),Z[g],(gx,gy),method='linear')
zf=np.where(np.isfinite(zg),zg,np.nanmedian(zg))
dy,dx=np.gradient(zf,0.5); hs=np.clip(0.5+(-dx+dy)*0.7,0,1)
lrm=zf-ndimage.uniform_filter(zf,40)
vmin=float(sys.argv[7]) if len(sys.argv)>7 else np.nanpercentile(zg,1); vmax=float(sys.argv[8]) if len(sys.argv)>8 else np.nanpercentile(zg,99)
n=int(H); top,_,_,_=stats.binned_statistic_2d(X,Y,Z,'max',bins=n,range=[[-H,H],[-H,H]])
dens,_,_=np.histogram2d(X[g],Y[g],bins=int(2*H/5),range=[[-H,H],[-H,H]])
fig,ax=plt.subplots(2,3,figsize=(20,13)); ax=ax.ravel(); E=[-H,H,-H,H]
ax[0].imshow(hs,origin='lower',extent=E,cmap='gray'); ax[0].set_title('ground-only TIN hillshade (0.5 m)')
ax[1].imshow(hs,origin='lower',extent=E,cmap='gray'); im=ax[1].imshow(np.clip(lrm,-1,1),origin='lower',extent=E,cmap='RdBu_r',alpha=0.55); plt.colorbar(im,ax=ax[1]); ax[1].set_title('local relief (20 m window), red=raised')
im=ax[2].imshow(zg,origin='lower',extent=E,cmap='terrain',vmin=vmin,vmax=vmax); plt.colorbar(im,ax=ax[2]); ax[2].set_title('ground z (m)')
im=ax[3].imshow(dens.T/25,origin='lower',extent=E,cmap='magma'); plt.colorbar(im,ax=ax[3]); ax[3].set_title('ground pts/m2 (5 m cells)')
im=ax[4].imshow(top.T-np.nanmedian(Z[g]),origin='lower',extent=E,cmap='Greens',vmin=0,vmax=35); plt.colorbar(im,ax=ax[4]); ax[4].set_title('max return above median ground (2 m)')
for a in range(0,180,45):
    t=np.radians(a); d=np.arange(-H,H,0.5); px=d*np.cos(t); py=d*np.sin(t)
    ii=np.clip(((py+H)/0.5).astype(int),0,zg.shape[0]-1); jj=np.clip(((px+H)/0.5).astype(int),0,zg.shape[1]-1)
    ax[5].plot(d,zg[ii,jj],label=f'{a} deg (E=0, N=90)'); ax[0].plot(px,py,lw=0.4)
ax[5].legend(); ax[5].grid(); ax[5].set_xlabel('m from centre'); ax[5].set_title('ground-TIN profiles through centre')
for a in ax[:5]: a.plot(0,0,'r+',ms=12)
plt.tight_layout(); plt.savefig(out+'_pc.png',dpi=65)
# raw-point W-E and S-N bands
fig,ax=plt.subplots(2,1,figsize=(16,9))
for k,(u,v,nm) in enumerate(((X,Y,'W-E'),(Y,X,'S-N'))):
    b=abs(v)<3; zt=np.median(Z[g]); keep=b&(Z<zt+40)
    ax[k].scatter(u[keep&~g],Z[keep&~g],s=1,c='green',label='non-ground'); ax[k].scatter(u[b&g],Z[b&g],s=4,c='k',label='ground')
    ax[k].set_title(f'{nm} raw points, 6 m band'); ax[k].legend(); ax[k].grid()
plt.tight_layout(); plt.savefig(out+'_rawprof.png',dpi=65); print(out+'_pc.png', out+'_rawprof.png')
