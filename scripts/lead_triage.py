"""Compact multi-lead triage from one 1518 LAZ granule (single pass over points).
Usage: lead_triage.py file.laz epsg outdir id:lat:lon:half_m [...]
Per lead: <outdir>/L<id>_tri.png (ground-TIN 0.5 m hillshade+LRM, ground pts/m2, canopy height, W-E & S-N TIN profiles,
Esri z17) and a stats line appended to <outdir>/stats.tsv."""
import sys, os, io, math, urllib.request, numpy as np, laspy
from pyproj import Transformer
from scipy.interpolate import griddata
from scipy import ndimage, stats
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f, epsg, od = sys.argv[1], int(sys.argv[2]), sys.argv[3]; os.makedirs(od, exist_ok=True)
T = Transformer.from_crs(4326, epsg, always_xy=True)
L = []
for a in sys.argv[4:]:
    i, la, lo, h = a.split(':'); x, y = T.transform(float(lo), float(la)); L.append(dict(id=i, lat=float(la), lon=float(lo), H=float(h), cx=x, cy=y, P=[]))
with laspy.open(f) as r:
    hd = r.header
    for p in r.chunk_iterator(3_000_000):
        x, y = np.asarray(p.x), np.asarray(p.y)
        for l in L:
            m = (abs(x-l['cx']) < l['H']+20) & (abs(y-l['cy']) < l['H']+20)
            if m.any(): l['P'].append((x[m]-l['cx'], y[m]-l['cy'], np.asarray(p.z)[m], np.asarray(p.classification)[m]))
def esri(lat, lon, z=17, n=3):
    N = 2**z; fx = (lon+180)/360*N; fy = (1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*N; cx, cy = int(fx), int(fy)
    im = Image.new('RGB', (256*n, 256*n))
    for i in range(n):
        for j in range(n):
            try:
                d = urllib.request.urlopen(urllib.request.Request(f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{cy-1+j}/{cx-1+i}', headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read()
                im.paste(Image.open(io.BytesIO(d)).convert('RGB'), (256*i, 256*j))
            except Exception: pass
    mpp = 156543.03*math.cos(math.radians(lat))/N; px, py = (fx-cx+1)*256, (fy-cy+1)*256
    return np.asarray(im), mpp, px, py
st = open(f'{od}/stats.tsv', 'a')
for l in L:
    H = l['H']
    if not l['P']:
        print(l['id'], 'NO POINTS (outside granule)'); st.write(f"{l['id']}\tnopoints\n"); continue
    X, Y, Z, C = map(np.concatenate, zip(*l['P'])); g = C == 2; rr = np.hypot(X, Y)
    def ring(a, b):
        m = (rr >= a) & (rr < b); ar = np.pi*(b*b-a*a); return (m & g).sum()/ar, m.sum()/ar
    rc = min(15, H/3); g0, a0 = ring(0, rc); g1, a1 = ring(rc, H)
    s = 0.5; gx, gy = np.meshgrid(np.arange(-H, H, s), np.arange(-H, H, s))
    if g.sum() < 50: print(l['id'], 'too few ground'); st.write(f"{l['id']}\tfewground\t{g.sum()}\n"); continue
    zg = griddata((X[g], Y[g]), Z[g], (gx, gy), method='linear'); zf = np.where(np.isfinite(zg), zg, np.nanmedian(zg))
    dy, dx = np.gradient(zf, s); hs = np.clip(0.5+(-dx+dy)*0.7, 0, 1)
    w = int(max(20, H/3)/s); lrm = zf-ndimage.uniform_filter(zf, w)
    zc = np.nanmedian(zg[np.hypot(gx, gy) < rc]); zr = np.nanmedian(zg[(np.hypot(gx, gy) > rc) & (np.hypot(gx, gy) < H)])
    n = int(H); top, _, _, _ = stats.binned_statistic_2d(X, Y, Z, 'max', bins=n, range=[[-H, H], [-H, H]])
    can = np.nanmedian(top)-np.nanmedian(Z[g])
    dens, _, _ = np.histogram2d(X[g], Y[g], bins=max(4, int(2*H/5)), range=[[-H, H], [-H, H]])
    line = f"{l['id']}\t{l['lat']}\t{l['lon']}\tgnd_c={g0:.2f}\tgnd_r={g1:.2f}\tall_c={a0:.1f}\tall_r={a1:.1f}\tdz_c-r={zc-zr:+.2f}\trelief={np.nanpercentile(zg,98)-np.nanpercentile(zg,2):.1f}\tcanopy_med={can:.1f}"
    print(line); st.write(line+'\n'); st.flush()
    fig, ax = plt.subplots(2, 3, figsize=(19, 12)); ax = ax.ravel(); E = [-H, H, -H, H]
    ax[0].imshow(hs, origin='lower', extent=E, cmap='gray'); ax[0].set_title(f"L{l['id']} ground TIN 0.5 m hillshade")
    ax[1].imshow(hs, origin='lower', extent=E, cmap='gray'); im = ax[1].imshow(np.clip(lrm, -1, 1), origin='lower', extent=E, cmap='RdBu_r', alpha=0.55); plt.colorbar(im, ax=ax[1]); ax[1].set_title(f'LRM {w*s:.0f} m, red raised (m)')
    im = ax[2].imshow(dens.T/25, origin='lower', extent=E, cmap='magma'); plt.colorbar(im, ax=ax[2]); ax[2].set_title('ground pts/m2 (5 m)')
    im = ax[3].imshow(top.T-np.nanmedian(Z[g]), origin='lower', extent=E, cmap='Greens', vmin=0, vmax=35); plt.colorbar(im, ax=ax[3]); ax[3].set_title('max return above median ground')
    d = np.arange(-H, H, s); k = len(d)//2
    ax[4].plot(d, zg[k, :], label='W-E'); ax[4].plot(d, zg[:, k], label='S-N'); ax[4].legend(); ax[4].grid(); ax[4].set_title('ground-TIN profiles (m)')
    try:
        im, mpp, px, py = esri(l['lat'], l['lon']); hp = H/mpp
        ax[5].imshow(im); ax[5].set_xlim(px-hp, px+hp); ax[5].set_ylim(py+hp, py-hp); ax[5].set_title('Esri World Imagery (same extent)')
        ax[5].plot(px, py, 'y+', ms=14)
    except Exception as e: ax[5].set_title(f'esri fail {e}')
    for a in ax[:4]: a.plot(0, 0, 'r+', ms=12)
    plt.tight_layout(); plt.savefig(f"{od}/L{l['id']}_tri.png", dpi=55); plt.close('all')
