"""Point-cloud check around a lead: per-class counts, ground density and a ground-only vs all-returns profile.
Usage: pc_check.py file.laz epsg lat lon half_m out.png"""
import sys, numpy as np, laspy
from pyproj import Transformer
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f, epsg, lat, lon, H, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
cx, cy = Transformer.from_crs(4326, epsg, always_xy=True).transform(lon, lat)
X = []; Y = []; Z = []; C = []
with laspy.open(f) as r:
    for p in r.chunk_iterator(2_000_000):
        x, y = np.asarray(p.x), np.asarray(p.y); m = (abs(x-cx) < H) & (abs(y-cy) < H)
        if m.any(): X.append(x[m]); Y.append(y[m]); Z.append(np.asarray(p.z)[m]); C.append(np.asarray(p.classification)[m])
X, Y, Z, C = map(np.concatenate, (X, Y, Z, C))
print('points', len(X), 'classes', dict(zip(*np.unique(C, return_counts=True))))
g = C == 2; area = (2*H)**2
print(f'ground density {g.sum()/area:.2f} pts/m2, all {len(X)/area:.2f} pts/m2')
# ground density inside r<40 m vs annulus 60-100 m
r = np.hypot(X-cx, Y-cy)
for a, b in ((0, 40), (60, 100)):
    m = (r >= a) & (r < b); ar = np.pi*(b*b-a*a)
    print(f'ring {a}-{b} m: ground {(m&g).sum()/ar:.3f}/m2, all {m.sum()/ar:.2f}/m2, ground z median {np.median(Z[m&g]) if (m&g).any() else float("nan"):.2f}')
fig, ax = plt.subplots(1, 3, figsize=(18, 6))
s = ax[0].scatter(X[g]-cx, Y[g]-cy, c=Z[g], s=1, cmap='terrain'); ax[0].set_title('ground (class 2) points, colour=z'); plt.colorbar(s, ax=ax[0]); ax[0].set_aspect('equal')
# ground density grid 5 m
n = int(2*H/5); Hh, _, _ = np.histogram2d(X[g]-cx, Y[g]-cy, bins=n, range=[[-H, H], [-H, H]])
im = ax[1].imshow(Hh.T/25, origin='lower', extent=[-H, H, -H, H], cmap='magma'); ax[1].set_title('ground pts per m2 (5 m cells)'); plt.colorbar(im, ax=ax[1])
band = abs(Y-cy) < 5
ax[2].scatter(X[band & ~g]-cx, Z[band & ~g], s=1, c='green', label='non-ground'); ax[2].scatter(X[band & g]-cx, Z[band & g], s=3, c='k', label='ground')
ax[2].set_title('W-E profile, 10 m wide band'); ax[2].legend(); ax[2].set_xlabel('m from centre')
plt.tight_layout(); plt.savefig(out, dpi=80); print(out)
