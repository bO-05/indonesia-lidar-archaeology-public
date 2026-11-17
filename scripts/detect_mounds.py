"""Automated mound detector on 1 m DTM: finds isolated compact raised features 10-50 m across,
>=0.7 m above their ~80 m surroundings, on relatively flat ground. Writes candidates CSV.
Usage: python detect_mounds.py DTM.tif out.csv prefix"""
import sys, csv, numpy as np, rasterio
from scipy import ndimage
from pyproj import Transformer
src, out, prefix = sys.argv[1:4]
tr = Transformer.from_crs(32748, 4326, always_xy=True)
with rasterio.open(src) as r:
    z = r.read(1).astype(np.float32); tf = r.transform
valid = np.isfinite(z) & (z > -1e30) & (z < 1e5)
zz = np.where(valid, z, np.nanmedian(np.where(valid, z, np.nan))).astype(np.float32); del z
base = ndimage.median_filter(zz[::4, ::4], size=21)  # ~84 m median at 4 m
base = ndimage.zoom(base, 4, order=1)[:zz.shape[0], :zz.shape[1]]
if base.shape != zz.shape:
    b2 = np.empty_like(zz); b2[:base.shape[0], :base.shape[1]] = base
    b2[base.shape[0]:, :] = b2[base.shape[0]-1:base.shape[0], :]; b2[:, base.shape[1]:] = b2[:, base.shape[1]-1:base.shape[1]]; base = b2
rel = ndimage.gaussian_filter(zz, 1.0) - base
gy, gx = np.gradient(ndimage.uniform_filter(zz, 15))
bgslope = np.degrees(np.arctan(np.hypot(gx, gy)))
mask = (rel > 0.7) & valid
lab, n = ndimage.label(mask)
objs = ndimage.find_objects(lab)
rows = []
for k, sl in enumerate(objs, 1):
    if sl is None: continue
    m = lab[sl] == k
    area = m.sum()
    if area < 80 or area > 2500: continue
    h, w = m.shape
    ext = max(h, w)
    if ext > 60 or ext < 10: continue
    fill = area / (h * w)
    if fill < 0.45: continue
    elong = max(h, w) / max(1, min(h, w))
    if elong > 2.2: continue
    peak = float(rel[sl][m].max())
    # ring check: surroundings within 30 m should be mostly below
    y0, x0 = sl[0].start, sl[1].start
    cy, cx = y0 + h // 2, x0 + w // 2
    ring = rel[max(0, cy-40):cy+40, max(0, cx-40):cx+40]
    others = (ring > 0.7).mean()
    if others > 0.25: continue  # part of larger high ground / dense mound field
    sl_bg = float(np.median(bgslope[max(0, cy-40):cy+40, max(0, cx-40):cx+40]))
    X, Y = tf * (cx, cy)
    lon, lat = tr.transform(X, Y)
    score = peak * fill / elong * (1 - others)
    rows.append([prefix, cx, cy, round(lat, 6), round(lon, 6), int(area), ext, round(peak, 2), round(fill, 2), round(elong, 2), round(others, 2), round(sl_bg, 1), round(score, 3)])
rows.sort(key=lambda r: -r[-1])
with open(out, 'w', newline='') as f:
    wr = csv.writer(f); wr.writerow(['src', 'px', 'py', 'lat', 'lon', 'area_m2', 'extent_m', 'height_m', 'fill', 'elong', 'crowding', 'bg_slope_deg', 'score']); wr.writerows(rows)
print(prefix, n, 'blobs ->', len(rows), 'candidates')
