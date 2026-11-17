"""ring_stability.py lat lon outdir [EPSG via env EPSG, default 32649] name=ground.laz[:class] ... : compare ground classifications around a ring feature.
Per setting: ground density by zone, nearest-ground-point distance in the ditch, azimuthal ring fit (24 rays),
cut/fill, 0.5 m TIN hillshade/LRM panel. Writes <outdir>/stability.tsv and stability_panel.png, profiles.png"""
import sys, numpy as np, laspy
from pyproj import Transformer
from scipy.interpolate import griddata
from scipy.spatial import cKDTree
from scipy import ndimage
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
lat, lon, od = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]; H = 110; s = 0.5
cx, cy = Transformer.from_crs(4326, int(__import__("os").environ.get("EPSG", "32649")), always_xy=True).transform(lon, lat)
sets = []
for a in sys.argv[4:]:
    n, f = a.split('=', 1); cls = None
    if f.endswith(':2'): f, cls = f[:-2], 2
    X = []; Y = []; Z = []
    with laspy.open(f) as r:
        for p in r.chunk_iterator(3_000_000):
            x, y = np.asarray(p.x), np.asarray(p.y); m = (abs(x-cx) < H) & (abs(y-cy) < H)
            if cls is not None: m &= np.asarray(p.classification) == cls
            if m.any(): X.append(x[m]-cx); Y.append(y[m]-cy); Z.append(np.asarray(p.z)[m])
    sets.append((n, *map(np.concatenate, (X, Y, Z))))
gx, gy = np.meshgrid(np.arange(-H, H, s), np.arange(-H, H, s)); D = np.hypot(gx, gy)
st = open(f'{od}/stability.tsv', 'w')
st.write('setting\tn_ground\tdens_interior_r<20\tdens_ditch_25-40\tdens_out_45-70\tditch_cells_nn>2m_pct\tditch_cells_nn>4m_pct\tcentre_dx\tcentre_dy\tditch_r_mean\tditch_r_sd\tclosure_pct\tinterior_above_ditch\touter_above_ditch\tcut_m3\tfill_m3\n')
fig, ax = plt.subplots(3, len(sets), figsize=(4.2*len(sets), 12.5), squeeze=False); prof = []
for k, (n, X, Y, Z) in enumerate(sets):
    R = np.hypot(X, Y); dens = lambda a, b: ((R >= a) & (R < b)).sum()/(np.pi*(b*b-a*a))
    zg = griddata((X, Y), Z, (gx, gy), 'linear'); nn, _ = cKDTree(np.c_[X, Y]).query(np.c_[gx.ravel(), gy.ravel()]); nn = nn.reshape(gx.shape)
    # centre = centroid of the high interior
    m = (D < 25) & np.isfinite(zg); hi = m & (zg > np.nanpercentile(zg[m], 80)); ox, oy = gx[hi].mean(), gy[hi].mean()
    rs = np.arange(0, 70, 0.5); rr = []; ok = []; ins = []; outs = []; P = []
    for az in range(0, 360, 15):
        t = np.radians(az); px, py = ox+rs*np.sin(t), oy+rs*np.cos(t)
        z = zg[((py+H)/s).astype(int), ((px+H)/s).astype(int)]; P.append(z)
        w = (rs > 15) & (rs < 50)
        if not np.isfinite(z[w]).any(): continue
        kk = np.nanargmin(np.where(w, z, np.nan)); top = np.nanmean(z[rs < 8]); out = np.nanmax(z[kk:kk+40])
        rr.append(rs[kk]); ins.append(top-z[kk]); outs.append(out-z[kk]); ok.append(top-z[kk] > 0.3 and out-z[kk] > 0.2)
    rr = np.array(rr); Dc = np.hypot(gx-ox, gy-oy); rm = rr.mean()
    ditch = (Dc > rm-6) & (Dc < rm+6); ref = np.nanmedian(zg[(Dc > rm+10) & (Dc < rm+25)])
    cut = np.nansum(np.clip(ref-zg[(Dc > rm-10) & (Dc < rm+8)], 0, None))*s*s; fill = np.nansum(np.clip(zg[Dc < rm-10]-ref, 0, None))*s*s
    st.write(f"{n}\t{len(X)}\t{dens(0,20):.3f}\t{dens(25,40):.3f}\t{dens(45,70):.3f}\t{100*(nn[ditch]>2).mean():.1f}\t{100*(nn[ditch]>4).mean():.1f}\t{ox:.1f}\t{oy:.1f}\t{rm:.1f}\t{rr.std():.1f}\t{100*np.mean(ok):.0f}\t{np.median(ins):.2f}\t{np.median(outs):.2f}\t{cut:.0f}\t{fill:.0f}\n")
    zf = np.where(np.isfinite(zg), zg, np.nanmedian(zg)); dy, dx = np.gradient(zf, s); hs = np.clip(0.5+(-dx+dy)*0.6, 0, 1)
    lrm = zf-ndimage.uniform_filter(zf, 80)
    ax[0, k].imshow(hs, cmap='gray', extent=[-H, H, -H, H], origin='lower'); ax[0, k].set_title(f'{n}: ground TIN 0.5 m\n{len(X)} pts, ditch r={rm:.0f}±{rr.std():.0f} m, closure {100*np.mean(ok):.0f}%', fontsize=9)
    ax[1, k].imshow(lrm, cmap='RdBu_r', vmin=-1.2, vmax=1.2, extent=[-H, H, -H, H], origin='lower'); ax[1, k].set_title('LRM 40 m (red=raised)', fontsize=9)
    ax[2, k].imshow(np.minimum(nn, 6), cmap='magma_r', extent=[-H, H, -H, H], origin='lower'); ax[2, k].set_title(f'dist to nearest ground pt (0-6 m)\nditch cells >2 m: {100*(nn[ditch]>2).mean():.0f}%', fontsize=9)
    for a in ax[:, k]: a.add_patch(plt.Circle((ox, oy), rm, fill=False, ec='lime', lw=0.6, ls='--'))
    prof.append((n, np.nanmean(np.array(P), 0), rs))
plt.tight_layout(); plt.savefig(f'{od}/stability_panel.png', dpi=80)
plt.figure(figsize=(7, 4))
for n, p, rs in prof: plt.plot(rs, p-np.nanmax(p), label=n)
plt.xlabel('m from interior centre'); plt.ylabel('mean ground z rel. summit (m)'); plt.legend(fontsize=7); plt.grid(alpha=.3); plt.title('Radial mean profile per ground setting')
plt.savefig(f'{od}/stability_profiles.png', dpi=90)
