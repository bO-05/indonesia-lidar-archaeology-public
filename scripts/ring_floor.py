"""ring_floor.py dtm.tif x y R : ditch-floor gradient test (min z along 36 rays within 0.55R-1.45R, sinusoid fit + permutation p)"""
import sys, numpy as np, rasterio
from rasterio.windows import from_bounds
f, X, Y, R = sys.argv[1], *map(float, sys.argv[2:5]); src = rasterio.open(f); W = 2*R+10
a = src.read(1, window=from_bounds(X-W, Y-W, X+W, Y+W, src.transform)).astype(float); a[(a == src.nodata) | (a < -500)] = np.nan
res = src.res[0]; c = np.array(a.shape)/2; rs = np.arange(0, 1.6*R, res)
fl = []; inn = []
for az in range(0, 360, 10):
    t = np.radians(az); ii = (c[0]-rs*np.cos(t)/res).astype(int); jj = (c[1]+rs*np.sin(t)/res).astype(int); p = a[ii, jj]
    w = (rs > 0.55*R) & (rs < 1.45*R); fl.append(np.nanmin(p[w])); inn.append(np.nanmedian(p[rs < 0.35*R]))
th = np.radians(np.arange(0, 360, 10)); z = np.array(fl); A = np.c_[np.ones_like(th), np.cos(th), np.sin(th)]
amp = lambda zz: np.hypot(*np.linalg.lstsq(A, zz, rcond=None)[0][1:])
o = amp(z); rng = np.random.default_rng(0); pp = np.mean([amp(rng.permutation(z)) >= o for _ in range(3000)])
print(f'floor range {np.ptp(z):.2f} sd {z.std():.2f} sinus amp {o:.2f} p={pp:.3f}; interior above floor {np.nanmedian(inn)-np.median(z):.2f}')
