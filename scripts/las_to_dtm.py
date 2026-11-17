"""Stream LAS files out of las.rar one at a time, grid ground points (class 2) into 1 m DTM GeoTIFFs
(min z of ground per cell, small gaps filled), delete the LAS. EPSG:32650 (UTM 50N)."""
import libarchive, laspy, numpy as np, rasterio, os, io, tempfile
from rasterio.transform import from_origin
from scipy import ndimage
os.makedirs('dtm2', exist_ok=True)
with libarchive.file_reader('las.rar') as a:
    for e in a:
        name = e.pathname
        if not name.endswith('.las') or (e.size or 0) < 1e6: continue
        out = f"dtm2/{name[:-4]}.tif"
        if os.path.exists(out): continue
        tmp = 'tmp.las'
        with open(tmp, 'wb') as f:
            for blk in e.get_blocks(): f.write(blk)
        las = laspy.read(tmp)
        cls = np.asarray(las.classification)
        g = cls == 2
        x, y, z = np.asarray(las.x)[g], np.asarray(las.y)[g], np.asarray(las.z)[g]
        if len(x) < 1000:
            os.remove(tmp); print(name, 'few ground', g.sum(), len(cls)); continue
        x0, y1 = np.floor(x.min()), np.ceil(y.max())
        W, H = int(np.ceil(x.max() - x0)) + 1, int(np.ceil(y1 - y.min())) + 1
        ci = ((y1 - y)).astype(int); cj = (x - x0).astype(int)
        dem = np.full((H, W), np.inf, np.float32)
        np.minimum.at(dem, (ci, cj), z.astype(np.float32))
        miss = ~np.isfinite(dem)
        from scipy.interpolate import LinearNDInterpolator
        vi, vj = np.nonzero(~miss)
        f = LinearNDInterpolator(np.c_[vi, vj], dem[vi, vj])
        mi, mj = np.nonzero(miss)
        filled = dem.copy(); filled[mi, mj] = f(mi, mj)
        dist = ndimage.distance_transform_edt(miss)
        filled[dist > 15] = np.nan
        with rasterio.open(out, 'w', driver='GTiff', height=H, width=W, count=1, dtype='float32', crs='EPSG:32650',
                           transform=from_origin(x0, y1, 1, 1), nodata=-3.4e38, compress='deflate') as o:
            o.write(np.where(np.isnan(filled), -3.4e38, filled).astype(np.float32), 1)
        print(name, 'pts', len(cls), 'ground', int(g.sum()), 'density', round(g.sum() / max(1, (~miss).sum()), 2), flush=True)
        os.remove(tmp)
