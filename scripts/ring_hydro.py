"""ring_hydro.py dtm05.tif x y outdir : ditch-floor elevation by azimuth + D8 flow accumulation context (2 m) around a ring"""
import numpy as _np
if not hasattr(_np, "in1d"): _np.in1d = _np.isin
import sys, numpy as np, rasterio
from rasterio.windows import from_bounds
from scipy import ndimage
from pysheds.grid import Grid
from pysheds.view import Raster, ViewFinder
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f, X, Y, od = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]; W = 500
src = rasterio.open(f); a = src.read(1, window=from_bounds(X-W, Y-W, X+W, Y+W, src.transform)).astype(float)
a[(a == src.nodata) | (a < -500)] = np.nan
a = np.nanmean(a[:a.shape[0]//4*4, :a.shape[1]//4*4].reshape(a.shape[0]//4, 4, a.shape[1]//4, 4), axis=(1, 3))  # 2 m
valid = np.isfinite(a); idx = ndimage.distance_transform_edt(~valid, return_distances=False, return_indices=True); z = a[tuple(idx)]
n = z.shape[0]; c = n//2; res = 2.0
# ditch floor by azimuth (min within r 20-45 m along each ray)
rs = np.arange(0, 60, 0.5); fl = []
for az in range(0, 360, 10):
    t = np.radians(az); p = z[(c - rs*np.cos(t)/res).astype(int), (c + rs*np.sin(t)/res).astype(int)]
    w = (rs > 20) & (rs < 45); k = np.where(w)[0][np.argmin(p[w])]; fl.append((az, rs[k], p[k]))
fl = np.array(fl)
vf = ViewFinder(affine=rasterio.Affine(res, 0, 0, 0, -res, n*res), shape=z.shape, nodata=np.nan)
g = Grid(viewfinder=vf); dem = Raster(z.astype(np.float64), viewfinder=vf)
pf = g.fill_pits(dem); fd = g.fill_depressions(pf); inf = g.resolve_flats(fd)
fdir = g.flowdir(inf); acc = g.accumulation(fdir)
depth = np.asarray(fd) - z  # depression depth (closed basins)
np.save(f'{od}/hydro_acc.npy', np.asarray(acc))
fig, ax = plt.subplots(1, 3, figsize=(18, 6)); e = [-W, W, -W, W]
ax[0].imshow(np.log10(np.asarray(acc)*4+1), cmap='Blues', extent=e); ax[0].set_title('D8 flow accumulation (log10 m2), 2 m cells, own SMRF DTM')
ax[1].imshow(np.where(depth > 0.05, depth, np.nan), cmap='viridis', vmin=0, vmax=1.5, extent=e); ax[1].set_title('closed-depression depth (m, filled - DTM)')
for a_ in ax[:2]:
    a_.add_patch(plt.Circle((0, 0), 33, fill=False, ec='r', lw=.8)); a_.set_xlim(-250, 250); a_.set_ylim(-250, 250)
ax[2].plot(fl[:, 0], fl[:, 2], 'o-'); ax[2].set_xlabel('azimuth (deg, from interior centre)'); ax[2].set_ylabel('ditch floor z (m)'); ax[2].grid(alpha=.3)
ax[2].set_title(f'ditch floor: range {np.ptp(fl[:,2]):.2f} m, sd {fl[:,2].std():.2f} m; radius {fl[:,1].mean():.1f}±{fl[:,1].std():.1f}')
plt.tight_layout(); plt.savefig(f'{od}/ring_hydro.png', dpi=70)
# where does the ditch drain? accumulation max on ring
A = np.asarray(acc); yy, xx = np.mgrid[:n, :n]; d = np.hypot(yy-c, xx-c)*res
ring = (d > 25) & (d < 42); out = (d > 42) & (d < 60)
print('ditch floor z by az:', ' '.join(f'{int(a)}:{zz:.2f}' for a, r, zz in fl))
print(f'max acc on ring {A[ring].max()*4:.0f} m2; ring depression depth max {depth[ring].max():.2f} m, frac ring cells in closed depressions(>0.1m) {(depth[ring]>0.1).mean():.2f}')
# outlets: ring cells whose flow goes to out zone with high acc
print(f'acc percentile 99 in 1km window {np.percentile(A,99)*4:.0f} m2; ring acc p90 {np.percentile(A[ring],90)*4:.0f}')
