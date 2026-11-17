"""ring_search.py dtm.tif out.tsv [res=2] : template + morphometric search for ring ditches around an inner mound
(L66-like: ditch radius ~15-60 m, closed/near-closed, outer side higher than ditch, interior raised) and for
square/rectilinear ditched enclosures (sides 30-120 m, rotations 0-75 deg).
Annular templates cancel planar slope, so no detrending is needed. Candidates -> per-ray morphometric check.
Columns: tile kind x y R_m S closure rcv inner_d outer_d leak cut fill slope_deg nodata theta relief"""
import sys, numpy as np, rasterio
from scipy import ndimage
from scipy.signal import fftconvolve
f, out = sys.argv[1], sys.argv[2]; res = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
src = rasterio.open(f); nd = src.nodata; k = int(round(res/src.res[0]))
tile = f.split('/')[-1].replace('_dtm.idw.tif', '').replace('.tif', '')
def disk(r0, r1):
    n = int(np.ceil(r1)); yy, xx = np.mgrid[-n:n+1, -n:n+1]; d = np.hypot(xx, yy); m = ((d >= r0) & (d < r1)).astype(np.float32); return m/m.sum()
def square(a0, a1, th):
    n = int(np.ceil(a1*1.5)); yy, xx = np.mgrid[-n:n+1, -n:n+1]; c, s = np.cos(th), np.sin(th)
    u, v = xx*c+yy*s, -xx*s+yy*c; d = np.maximum(abs(u), abs(v)); m = ((d >= a0) & (d < a1)).astype(np.float32); return m/m.sum()
RS = [15, 20, 26, 33, 42, 52, 60]
SQ = [15, 25, 40, 60]  # half-side m
BS = 1500; OV = 160
rows = []
H, W = src.height//k, src.width//k
for bi in range(0, H, BS):
    for bj in range(0, W, BS):
        r0, c0 = max(0, bi-OV), max(0, bj-OV); r1, c1 = min(H, bi+BS+OV), min(W, bj+BS+OV)
        a = src.read(1, window=((r0*k, r1*k), (c0*k, c1*k))).astype(np.float32)
        a = a[:(a.shape[0]//k)*k, :(a.shape[1]//k)*k]
        bad = (a == nd) | ~np.isfinite(a) | (a < -500)
        if bad.mean() > 0.97: continue
        a[bad] = np.nan
        if k > 1:
            a = np.nanmean(a.reshape(a.shape[0]//k, k, a.shape[1]//k, k), axis=(1, 3))
        badk = ~np.isfinite(a)
        if badk.all(): continue
        idx = ndimage.distance_transform_edt(badk, return_distances=False, return_indices=True)
        z = a[tuple(idx)]
        sl = np.degrees(np.arctan(np.hypot(*np.gradient(ndimage.uniform_filter(z, int(100/res)), res))))
        badf = ndimage.uniform_filter(badk.astype(np.float32), int(150/res))
        for kind, sizes in (('ring', RS), ('rect', SQ)):
            best = np.full(z.shape, -9, np.float32); bR = np.zeros(z.shape, np.float32); bT = np.zeros(z.shape, np.float32)
            for R in sizes:
                Rp = R/res
                ths = [0.0] if kind == 'ring' else [np.radians(t) for t in (0, 15, 30, 45, 60, 75)]
                for th in ths:
                    if kind == 'ring': K = (disk(0, 0.55*Rp), disk(0.8*Rp, 1.2*Rp), disk(1.4*Rp, 1.8*Rp))
                    else: K = (square(0, 0.6*Rp, th), square(0.8*Rp, 1.15*Rp, th), square(1.35*Rp, 1.7*Rp, th))
                    ci, cr, co = (fftconvolve(z, kk, mode='same') for kk in K)
                    S = np.minimum(ci-cr, (co-cr)*1.5)
                    upd = S > best; best[upd] = S[upd]; bR[upd] = R; bT[upd] = th
            mx = ndimage.maximum_filter(best, size=int(30/res))
            pk = np.argwhere((best == mx) & (best > 0.25) & (badf < 0.05) & (sl < 8))
            # restrict to block core
            for (i, j) in pk:
                gi, gj = r0+i, c0+j
                if not (bi <= gi < bi+BS and bj <= gj < bj+BS): continue
                R = bR[i, j]; Rp = R/res; th = bT[i, j]
                # per-ray morphometry
                az = np.radians(np.arange(0, 360, 15)); rr = np.arange(0, 2.3*Rp, 0.5)
                ok = []; rk = []; leakn = 0
                zin = []
                for t in az:
                    if kind == 'ring': rs = rr
                    else:
                        u = abs(np.cos(t-th)); v = abs(np.sin(t-th)); rs = rr  # sample along ray, ditch expected at Rp/max(u,v)
                    yi = np.clip((i - rs*np.cos(t)).round().astype(int), 0, z.shape[0]-1); xj = np.clip((j + rs*np.sin(t)).round().astype(int), 0, z.shape[1]-1)
                    p = z[yi, xj]
                    exp = Rp if kind == 'ring' else Rp/max(abs(np.cos(t-th)), abs(np.sin(t-th)))
                    w = (rs > 0.5*exp) & (rs < 1.5*exp)
                    if not w.any(): continue
                    kk = np.where(w)[0][np.argmin(p[w])]; zin.append(np.mean(p[rs < 0.35*Rp]))
                    outer = p[kk:min(len(p), kk+int(0.7*exp)+1)].max(); inner = np.mean(p[rs < 0.35*Rp])
                    ok.append((inner-p[kk] > 0.2) and (outer-p[kk] > 0.15)); rk.append(rs[kk]/exp)
                    # leak: is ground still low (within 40% of ditch depth) at 1.8x the ditch radius?
                    far = p[min(len(p)-1, int(min(1.8*rs[kk], rs[-1])/0.5))]
                    if far - p[kk] < 0.4*max(outer-p[kk], 0.01): leakn += 1
                if len(ok) < 20: continue
                ok = np.array(ok); closure = ok.mean(); rk = np.array(rk); rcv = rk.std()/rk.mean()
                # cut/fill vs. outer reference
                n = int(1.8*Rp)+1; ys, xs = slice(max(0, i-n), min(z.shape[0], i+n+1)), slice(max(0, j-n), min(z.shape[1], j+n+1))
                zz = z[ys, xs]; yy, xx = np.mgrid[ys, xs]; d = np.hypot(yy-i, xx-j)
                if kind == 'rect':
                    c, s = np.cos(th), np.sin(th); u, v = (xx-j)*c+(yy-i)*s, -(xx-j)*s+(yy-i)*c; d = np.maximum(abs(u), abs(v))
                ref = np.median(zz[(d >= 1.35*Rp) & (d < 1.8*Rp)])
                cut = np.clip(ref-zz[(d >= 0.7*Rp) & (d < 1.3*Rp)], 0, None).sum()*res*res
                fill = np.clip(zz[d < 0.7*Rp]-ref, 0, None).sum()*res*res
                inner_d = np.median(zz[d < 0.35*Rp]) - np.median(zz[(d >= 0.8*Rp) & (d < 1.2*Rp)])
                outer_d = ref - np.median(zz[(d >= 0.8*Rp) & (d < 1.2*Rp)])
                x, y = src.xy(gi*k + k/2, gj*k + k/2)
                rows.append((tile, kind, round(x, 1), round(y, 1), R, round(float(best[i, j]), 3), round(closure, 2), round(rcv, 2),
                             round(float(inner_d), 2), round(float(outer_d), 2), round(leakn/24, 2), int(cut), int(fill),
                             round(float(sl[i, j]), 1), round(float(badf[i, j]), 3), round(np.degrees(th)), round(float(np.ptp(zz)),2)))
with open(out, 'w') as o:
    o.write('tile\tkind\tx\ty\tR_m\tS\tclosure\trcv\tinner_d\touter_d\tleak\tcut\tfill\tslope\tnodata\ttheta\trelief\n')
    for r in rows: o.write('\t'.join(map(str, r))+'\n')
print(tile, len(rows))
