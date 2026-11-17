"""ring_filter.py out.tsv in1.tsv [...] : apply L66-calibrated morphometric filters to ring_search output, rank, de-duplicate.
L66 calibration (own SMRF DTM): ring R33 S0.74 closure0.96 rcv0.12 inner_d1.9 outer_d0.62 leak0.25 cut2067 fill1194 slope0.4 relief3.6"""
import sys, pandas as pd, numpy as np
d = pd.concat([pd.read_csv(f, sep='\t') for f in sys.argv[2:]], ignore_index=True)
d['fc'] = d.fill/d.cut.clip(lower=1)
ring = (d.kind == 'ring') & (d.closure >= 0.8) & (d.rcv <= 0.2) & d.inner_d.between(0.5, 4) & d.outer_d.between(0.2, 3) & (d.leak <= 0.35) \
       & d.fc.between(0.25, 3) & (d.slope <= 4) & (d.relief <= 12) & (d.nodata < 0.02) & (d.S >= 0.4)
rect = (d.kind == 'rect') & (d.closure >= 0.85) & (d.rcv <= 0.2) & d.inner_d.between(0.3, 4) & d.outer_d.between(0.2, 3) & (d.leak <= 0.3) \
       & d.fc.between(0.25, 3) & (d.slope <= 4) & (d.relief <= 12) & (d.nodata < 0.02) & (d.S >= 0.4)
k = d[ring | rect].copy(); k['score'] = k.S*k.closure*(1-k.leak)*(1-k.rcv)
k = k.sort_values('score', ascending=False)
keep = []
for _, r in k.iterrows():
    if any((r.tile == q.tile) and np.hypot(r.x-q.x, r.y-q.y) < max(r.R_m, q.R_m)*1.5 for q in keep): continue
    keep.append(r)
o = pd.DataFrame(keep); o.to_csv(sys.argv[1], sep='\t', index=False)
print(f'{len(d)} raw -> {ring.sum()} ring + {rect.sum()} rect pass -> {len(o)} unique'); print(o.head(40).to_string())
