"""ring_chips.py hits.tsv dtm_dir_or_file outprefix [n=30] [tag] : contact sheets (5 hits per sheet; per hit hillshade, LRM, two
profiles) for ranked ring_search hits. Tiles resolved as <dtm_dir>/<tile>_dtm.idw.tif unless a file is given."""
import sys, os, numpy as np, pandas as pd, rasterio
from rasterio.windows import from_bounds
from scipy import ndimage
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = pd.read_csv(sys.argv[1], sep='\t'); src_arg = sys.argv[2]; op = sys.argv[3]; n = int(sys.argv[4]) if len(sys.argv) > 4 else 30
tag = sys.argv[5] if len(sys.argv) > 5 else 'H'
d = d.head(n).reset_index(drop=True)
for s0 in range(0, len(d), 5):
    sub = d.iloc[s0:s0+5]; fig, ax = plt.subplots(len(sub), 3, figsize=(14, 4.3*len(sub)), squeeze=False)
    for r, (ix, h) in enumerate(sub.iterrows()):
        f = src_arg if src_arg.endswith('.tif') else (f'{src_arg}/{h.tile}_dtm.idw.tif' if os.path.exists(f'{src_arg}/{h.tile}_dtm.idw.tif') else f'{src_arg}/{h.tile}.tif')
        src = rasterio.open(f); W = max(120, 3.2*h.R_m)
        a = src.read(1, window=from_bounds(h.x-W, h.y-W, h.x+W, h.y+W, src.transform)).astype(float)
        a[(a == src.nodata) | (a < -500)] = np.nan; res = src.res[0]
        if res < 1: a = ndimage.zoom(np.nan_to_num(a, nan=np.nanmedian(a)), res)  # to ~1 m
        res = 1.0 if src.res[0] < 1 else res
        af = np.where(np.isfinite(a), a, np.nanmedian(a)); dy, dx = np.gradient(af, res); hs = np.clip(0.5+(-dx+dy)*0.5, 0, 1)
        lrm = af-ndimage.uniform_filter(af, int(max(40, 1.6*h.R_m)/res))
        e = [-W, W, -W, W]
        ax[r, 0].imshow(hs, cmap='gray', extent=e); ax[r, 0].add_patch(plt.Circle((0, 0), h.R_m, fill=False, ec='r', lw=.7, ls='--'))
        ax[r, 0].set_title(f'{tag}{s0+r+1} {h.kind} R{h.R_m:.0f} score {h.score:.2f}\n{h.tile} clos {h.closure} in {h.inner_d} out {h.outer_d} leak {h.leak} f/c {h.fc:.2f}', fontsize=8)
        v = np.nanpercentile(abs(lrm), 98); ax[r, 1].imshow(lrm, cmap='RdBu_r', vmin=-v, vmax=v, extent=e); ax[r, 1].set_title(f'LRM ±{v:.1f} m', fontsize=8)
        c = a.shape[0]//2; xs = np.linspace(-W, W, a.shape[1])
        ax[r, 2].plot(xs, a[c, :], label='W-E'); ax[r, 2].plot(np.linspace(-W, W, a.shape[0]), a[::-1, a.shape[1]//2], label='S-N')
        ax[r, 2].axvline(-h.R_m, c='gray', lw=.5); ax[r, 2].axvline(h.R_m, c='gray', lw=.5); ax[r, 2].legend(fontsize=7); ax[r, 2].grid(alpha=.3)
    plt.tight_layout(); plt.savefig(f'{op}_{s0//5}.png', dpi=62); plt.close()
