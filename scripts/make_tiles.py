"""Turn a 1 m lidar DTM into archaeology-friendly visualisation tiles (windowed, memory-safe).
Each tile: multi-direction hillshade (grey, 2x vertical exaggeration) overlaid with a 25 m local
relief model (DTM - 25 m mean), red = raised, blue = sunken (+-1 m). White = no data.
Processes the DTM in windows of 3 tiles x 3 tiles (+32 px margin) so large grids fit in RAM.
Hillshade contrast is stretched per window (1-99 percentile) instead of over the whole DTM.
Output PNG tiles + <prefix>_index.csv with tile bounds (UTM) and centre lat/lon.
Usage: python make_tiles.py DTM.tif outdir prefix [tile_m=750]
"""
import sys, os, csv
import numpy as np, rasterio
from rasterio.windows import Window
from scipy import ndimage
from PIL import Image, ImageDraw
from pyproj import Transformer

src, outdir, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
T = int(sys.argv[4]) if len(sys.argv) > 4 else 750
os.makedirs(outdir, exist_ok=True)

def hillshade(a, az, alt=35):
    gy, gx = np.gradient(a)
    slope = np.pi/2 - np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    azr, altr = np.radians(az), np.radians(alt)
    return (np.sin(altr)*np.sin(slope) + np.cos(altr)*np.cos(slope)*np.cos(azr - aspect))

rows = []
M, S = 32, 3 * T
with rasterio.open(src) as r:
    tf = r.transform
    tr = Transformer.from_crs(r.crs.to_epsg() or 32748, 4326, always_xy=True)
    H, W = r.height, r.width
    for wi in range(0, H, S):
        for wj in range(0, W, S):
            i0, j0 = max(wi - M, 0), max(wj - M, 0)
            i1, j1 = min(wi + S + M, H), min(wj + S + M, W)
            z = r.read(1, window=Window(j0, i0, j1 - j0, i1 - i0)).astype(np.float32)
            valid = np.isfinite(z) & (z > -1e30) & (z < 1e5) & (z > -9000)
            if r.nodata is not None: valid &= z != r.nodata
            if valid.mean() < 0.01 and not valid.any():
                continue
            ci, cj = wi - i0, wj - j0
            ch, cw = min(S, H - wi), min(S, W - wj)
            vcore = valid[ci:ci+ch, cj:cj+cw]
            if not any(vcore[a:a+T, b:b+T].mean() >= 0.15 for a in range(0, ch, T) for b in range(0, cw, T)):
                continue
            zz = np.where(valid, z, np.median(z[valid])).astype(np.float32); del z
            hs = np.zeros_like(zz)
            for az in (315, 45, 135, 225, 0, 90):
                hs += hillshade(zz * 2.0, az)
            hs /= 6
            p1, p99 = np.percentile(hs[valid], 1), np.percentile(hs[valid], 99)
            hs = np.clip((hs - p1) / max(p99 - p1, 1e-6), 0, 1)
            l = np.clip((zz - ndimage.uniform_filter(zz, size=25)) / 1.0, -1, 1)
            R = hs*0.6 + np.clip(l, 0, 1)*0.4
            G = hs*0.6
            Bc = hs*0.6 + np.clip(-l, 0, 1)*0.4
            rgb = np.stack([R, G, Bc], -1)
            rgb = (np.clip(rgb / 1.0, 0, 1) * 255).astype(np.uint8)
            rgb[~valid] = (255, 255, 255)
            rgb = rgb[ci:ci+ch, cj:cj+cw]
            del zz, hs, l, R, G, Bc
            for a in range(0, ch, T):
                for b in range(0, cw, T):
                    v = vcore[a:a+T, b:b+T]
                    if v.mean() < 0.15: continue
                    i, j = wi + a, wj + b
                    im = Image.fromarray(np.ascontiguousarray(rgb[a:a+T, b:b+T]))
                    if T != 750: im = im.resize((750, 750))
                    d = ImageDraw.Draw(im); px = 100 * im.width / T
                    d.rectangle([10, im.height-20, 10+px, im.height-14], fill=(0, 0, 0))
                    name = f"{prefix}_r{i//T:03d}_c{j//T:03d}"
                    im.save(os.path.join(outdir, name + ".png"), optimize=True)
                    x0, y0 = tf * (j, i); x1, y1 = tf * (j+T, i+T)
                    lon, lat = tr.transform((x0+x1)/2, (y0+y1)/2)
                    rows.append([name, i, j, x0, y0, x1, y1, round(lat, 6), round(lon, 6), round(float(v.mean()), 2)])
rows.sort()
with open(os.path.join(outdir, f"{prefix}_index.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["tile", "row_px", "col_px", "x0", "y0", "x1", "y1", "lat_c", "lon_c", "valid_frac"]); w.writerows(rows)
print(prefix, len(rows), "tiles")
