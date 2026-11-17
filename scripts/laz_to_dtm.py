"""NASA CMS Kalimantan LAZ (ground = class 2) -> 1 m DTM GeoTIFF.
Memory-safe version (Nov 2026): streams points in chunks, keeps one float32 grid,
then gap-fills and writes in 2000x2000 blocks (64 px margin) so big sparse grids
(e.g. Polygon_211_utm_49N_3, 10685x9751) fit in ~1-1.5 GB RAM.
Gap fill: pyramid fill (coarser block means), only within 20 m of data, filled cells Gaussian-smoothed (sigma 2).
Usage: python laz_to_dtm.py in.laz out.tif"""
import sys, re, os, numpy as np, laspy, rasterio
from rasterio.transform import from_origin
from rasterio.windows import Window
from scipy import ndimage
src, out = sys.argv[1], sys.argv[2]
m = re.search(r'utm_(\d+)([NS])', src)
epsg = (32600 if m.group(2) == 'N' else 32700) + int(m.group(1))
with laspy.open(src) as f:
    h = f.header
    x0, y1 = np.floor(h.mins[0]), np.ceil(h.maxs[1])
    W, H = int(np.ceil(h.maxs[0] - x0)) + 1, int(np.ceil(y1 - h.mins[1])) + 1
    dem = np.full(H * W, np.inf, np.float32)
    for pts in f.chunk_iterator(2_000_000):
        g = np.asarray(pts.classification) == 2
        if not g.any(): continue
        x, y = np.asarray(pts.x)[g], np.asarray(pts.y)[g]
        z = np.asarray(pts.z)[g].astype(np.float32)
        idx = (y1 - y).astype(np.int64) * W + (x - x0).astype(np.int64)
        del x, y
        o = np.lexsort((z, idx)); idx, z = idx[o], z[o]
        first = np.r_[True, idx[1:] != idx[:-1]]
        u, zm = idx[first], z[first]
        dem[u] = np.minimum(dem[u], zm)
        del idx, z, o, first, u, zm, pts
dem = dem.reshape(H, W)
valid_all = np.isfinite(dem)
print(src, 'grid', H, W, 'valid frac', round(float(valid_all.mean()), 3), flush=True)
del valid_all
B, M = 2000, 64
tmp = out + '.part'
with rasterio.open(tmp, 'w', driver='GTiff', height=H, width=W, count=1, dtype='float32', crs=f'EPSG:{epsg}',
                   transform=from_origin(x0, y1, 1, 1), nodata=-3.4e38, compress='deflate', tiled=True,
                   blockxsize=256, blockysize=256, BIGTIFF='IF_SAFER') as o:
    for i in range(0, H, B):
        for j in range(0, W, B):
            i0, j0 = max(i - M, 0), max(j - M, 0)
            i1, j1 = min(i + B + M, H), min(j + B + M, W)
            d = dem[i0:i1, j0:j1]
            valid = np.isfinite(d)
            ci0, cj0 = i - i0, j - j0
            ch, cw = min(B, H - i), min(B, W - j)
            if not valid.any():
                o.write(np.full((ch, cw), -3.4e38, np.float32), 1, window=Window(j, i, cw, ch)); continue
            h_, w_ = d.shape
            filled = np.where(valid, d, np.nan).astype(np.float32)
            for k in (2, 4, 8, 16, 32):
                Hc, Wc = -(-h_ // k), -(-w_ // k)
                pad = np.full((Hc * k, Wc * k), np.nan, np.float32); pad[:h_, :w_] = np.where(valid, d, np.nan)
                with np.errstate(all='ignore'):
                    import warnings; warnings.simplefilter('ignore')
                    cm = np.nanmean(pad.reshape(Hc, k, Wc, k), axis=(1, 3))
                up = np.repeat(np.repeat(cm, k, 0), k, 1)[:h_, :w_]
                hole = np.isnan(filled); filled[hole] = up[hole]
                del pad, cm, up
                if not np.isnan(filled).any(): break
            sm = ndimage.gaussian_filter(np.nan_to_num(filled, nan=float(np.nanmedian(filled))), 2.0)
            filled = np.where(valid, filled, sm)
            dist = ndimage.distance_transform_edt(~valid)
            filled[dist > 20] = np.nan
            core = filled[ci0:ci0 + ch, cj0:cj0 + cw]
            o.write(np.where(np.isnan(core), -3.4e38, core).astype(np.float32), 1, window=Window(j, i, cw, ch))
            del filled, sm, dist, valid
os.replace(tmp, out)
