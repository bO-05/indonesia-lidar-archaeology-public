"""d8_quads.py tile outdir : smoothed LRM (~500 m) quadrant PNGs (1000 px each, ~13 m/px) with 0.05deg grid labels"""
import sys,numpy as np,os; sys.path.insert(0,'scripts'); from d8_relief import *
from scipy import ndimage; from PIL import Image, ImageDraw
t,od=sys.argv[1],sys.argv[2]; os.makedirs(od,exist_ok=True)
r,a,dx,dy=load(f'data/demnas8/DEMNAS_{t}_v1.0.tif'); f=fill(a); g=ndimage.gaussian_filter(f,1.5)
bg=ndimage.median_filter(g[::2,::2],size=31); bg=ndimage.zoom(bg,2,order=1)[:g.shape[0],:g.shape[1]]
s=g-bg; np.save(f'/tmp/q_{t}.npy',s.astype('float32'))
v=np.clip((s+3)/6*255,0,255).astype('uint8'); H,W=v.shape
for i in range(2):
  for j in range(2):
    im=Image.fromarray(v[i*H//2:(i+1)*H//2, j*W//2:(j+1)*W//2]).resize((1000,1000)).convert('RGB'); d=ImageDraw.Draw(im)
    for k in range(1,5):
      d.line([k*200,0,k*200,1000],fill=(255,0,0)); d.line([0,k*200,1000,k*200],fill=(255,0,0))
    for a_ in range(5):
      for b_ in range(5): d.text((a_*200+3,b_*200+3),f'{i}{j}{b_}{a_}',fill=(255,255,0))
    im.save(f'{od}/q{i}{j}.png')
print(t,'done')
