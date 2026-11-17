"""Zoom crop around a lat/lon from a 1 m DTM: hillshade + local relief (red raised, blue sunken),
contours every 1 m, plus a W-E and N-S elevation profile through the centre.
Usage: python zoom.py DTM.tif lat lon half_m out.png [lrm_window=15] [contour_m=1]"""
import sys, numpy as np, rasterio
from rasterio.windows import Window
from scipy import ndimage
from pyproj import Transformer
from PIL import Image, ImageDraw
dtm, lat, lon, half, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
lw = int(sys.argv[6]) if len(sys.argv) > 6 else 15
ci = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
with rasterio.open(dtm) as r:
    x, y = Transformer.from_crs(4326, r.crs, always_xy=True).transform(lon, lat)
    row, col = r.index(x, y)
    m = 40
    z = r.read(1, window=Window(col - half - m, row - half - m, 2*(half+m), 2*(half+m)), boundless=True, fill_value=np.nan).astype(np.float32)
    if r.nodata is not None: z[z == r.nodata] = np.nan
    z[z < -1000] = np.nan
v = np.isfinite(z) & (z > -1e30)
zz = np.where(v, z, np.nanmedian(np.where(v, z, np.nan)))
def hs(a, az, alt=35):
    gy, gx = np.gradient(a); s = np.pi/2 - np.arctan(np.hypot(gx, gy)); asp = np.arctan2(-gx, gy)
    return np.sin(np.radians(alt))*np.sin(s) + np.cos(np.radians(alt))*np.cos(s)*np.cos(np.radians(az) - asp)
h = sum(hs(zz*3, a) for a in (315, 45, 135, 225)) / 4
h = np.clip((h - np.percentile(h, 1)) / (np.percentile(h, 99) - np.percentile(h, 1) + 1e-6), 0, 1)
l = np.clip((zz - ndimage.uniform_filter(zz, lw)) / 0.6, -1, 1)
rgb = np.stack([h*0.6 + np.clip(l, 0, 1)*0.4, h*0.6, h*0.6 + np.clip(-l, 0, 1)*0.4], -1)
cont = np.zeros_like(v)
zi = np.floor(zz / ci); cont[:-1] |= zi[:-1] != zi[1:]; cont[:, :-1] |= zi[:, :-1] != zi[:, 1:]
rgb[cont] = rgb[cont]*0.5 + np.array([0.9, 0.9, 0.2])*0.5
rgb[~v] = 1
rgb = rgb[m:-m, m:-m]; zc = zz[m:-m, m:-m]
S = 700; im = Image.fromarray((rgb*255).astype(np.uint8)).resize((S, S), Image.NEAREST if half < 120 else Image.BILINEAR)
canvas = Image.new('RGB', (S + 260, S + 30), 'white'); canvas.paste(im, (0, 0)); d = ImageDraw.Draw(canvas)
sc = S / (2*half); d.line([S//2-6, S//2, S//2+6, S//2], fill=(0, 255, 0)); d.line([S//2, S//2-6, S//2, S//2+6], fill=(0, 255, 0))
bar = 50 if half <= 200 else 100; d.rectangle([10, S-20, 10+bar*sc, S-14], fill=(0, 0, 0)); d.text((12, S-34), f'{bar} m', fill=(0, 0, 0))
d.text((5, S+8), f'{lat:.6f},{lon:.6f}  half={half} m  contours {ci:g} m  LRM {lw} m', fill=(0, 0, 0))
for k, (prof, lab) in enumerate([(zc[half, :], 'W-E'), (zc[:, half], 'N-S')]):
    y0 = 20 + k*340; lo, hi = prof.min(), prof.max(); rng = max(hi - lo, 1)
    pts = [(S + 20 + i*220/len(prof), y0 + 280 - (p - lo)/rng*260) for i, p in enumerate(prof)]
    d.line(pts, fill=(200, 0, 0)); d.text((S + 20, y0 - 15), f'{lab} profile {lo:.1f}-{hi:.1f} m', fill=(0, 0, 0))
canvas.save(out); print(out, 'elev range', float(np.nanmin(zc)), float(np.nanmax(zc)))
