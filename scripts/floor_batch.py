"""floor_batch.py hits.tsv out.tsv dtm_dir : add ditch-floor gradient test (amp, p) to every hit"""
import sys, numpy as np, pandas as pd, rasterio
from rasterio.windows import from_bounds
d = pd.read_csv(sys.argv[1], sep='\t'); out = []
th = np.radians(np.arange(0, 360, 10)); A = np.c_[np.ones_like(th), np.cos(th), np.sin(th)]
amp = lambda zz: np.hypot(*np.linalg.lstsq(A, zz, rcond=None)[0][1:]); rng = np.random.default_rng(0)
for _, h in d.iterrows():
    import os; fp = f'{sys.argv[3]}/{h.tile}_dtm.idw.tif'; fp = fp if os.path.exists(fp) else f'{sys.argv[3]}/{h.tile}.tif'; src = rasterio.open(fp); R = h.R_m; W = 2*R+10
    a = src.read(1, window=from_bounds(h.x-W, h.y-W, h.x+W, h.y+W, src.transform)).astype(float); a[(a == src.nodata) | (a < -500)] = np.nan
    res = src.res[0]; c = np.array(a.shape)/2; rs = np.arange(0, 1.6*R, res); fl = []
    for t in th:
        ii = np.clip((c[0]-rs*np.cos(t)/res).astype(int), 0, a.shape[0]-1); jj = np.clip((c[1]+rs*np.sin(t)/res).astype(int), 0, a.shape[1]-1)
        p = a[ii, jj]; w = (rs > 0.55*R) & (rs < 1.45*R); fl.append(np.nanmin(p[w]) if np.isfinite(p[w]).any() else np.nan)
    z = np.array(fl)
    if np.isnan(z).any(): out.append((np.nan, np.nan, np.nan)); continue
    o = amp(z); out.append((round(o, 2), round(float(np.mean([amp(rng.permutation(z)) >= o for _ in range(1000)])), 3), round(z.std(), 2)))
d['floor_amp'], d['floor_p'], d['floor_sd'] = zip(*out); d.to_csv(sys.argv[2], sep='\t', index=False)
print(d[['tile', 'kind', 'x', 'y', 'R_m', 'score', 'floor_amp', 'floor_p', 'floor_sd', 'slope', 'relief']].sort_values('floor_p', ascending=False).head(25).to_string())
print((d.floor_p > 0.1).sum(), 'of', len(d), 'have ungraded floors (p>0.1)')
