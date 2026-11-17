"""floor_compare.py out.png [cases.tsv] : ditch-floor grading plot for a candidate ring vs natural ring analogues"""
import sys, numpy as np, rasterio
from rasterio.windows import from_bounds
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
# Cases (label, dtm path, x, y, R in the DTM CRS) are not published because they contain exact positions.
# Provide them locally: floor_compare.py out.png cases.tsv
# (tab-separated: label<TAB>dtm<TAB>x<TAB>y<TAB>R)
if len(sys.argv) < 3: sys.exit("cases.tsv required: exact site coordinates are not published")
cases = sys.argv[2]
C=[(l,f,float(x),float(y),float(r)) for l,f,x,y,r in (ln.rstrip('\n').split('\t') for ln in open(cases) if ln.strip())]
th=np.radians(np.arange(0,360,10));A=np.c_[np.ones_like(th),np.cos(th),np.sin(th)];amp=lambda z:np.hypot(*np.linalg.lstsq(A,z,rcond=None)[0][1:])
rng=np.random.default_rng(0);plt.figure(figsize=(9,5))
for nm,f,X,Y,R in C:
    s=rasterio.open(f);W=2*R+10;a=s.read(1,window=from_bounds(X-W,Y-W,X+W,Y+W,s.transform)).astype(float);a[(a==s.nodata)|(a<-500)]=np.nan
    res=s.res[0];c=np.array(a.shape)/2;rs=np.arange(0,1.6*R,res);z=[]
    for t in th:
        p=a[(c[0]-rs*np.cos(t)/res).astype(int),(c[1]+rs*np.sin(t)/res).astype(int)];w=(rs>.55*R)&(rs<1.45*R);z.append(np.nanmin(p[w]))
    z=np.array(z);o=amp(z);pp=np.mean([amp(rng.permutation(z))>=o for _ in range(3000)])
    plt.plot(np.degrees(th),z-z.mean(),'o-' if 'L66' in nm else '.--',lw=2 if 'L66' in nm else 1,label=f'{nm}: grade amp {o:.2f} m, p={pp:.3f}')
    print(nm, round(o,2), pp, round(z.std(),2))
plt.xlabel('azimuth around ring centre (deg)');plt.ylabel('ditch floor z minus mean (m)');plt.legend(fontsize=7);plt.grid(alpha=.3)
plt.title('Ditch-floor grading: natural gully rings slope toward an outlet; L66 floor is level within noise',fontsize=9)
plt.tight_layout();plt.savefig(sys.argv[1],dpi=85)
