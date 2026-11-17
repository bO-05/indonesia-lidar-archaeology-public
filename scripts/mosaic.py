"""2x2 contact sheets (each tile 600 px, labelled) for faster visual review.
Usage: mosaic.py listfile outdir"""
import sys, os
from PIL import Image, ImageDraw
paths = [l.strip() for l in open(sys.argv[1]) if l.strip()]; out = sys.argv[2]; os.makedirs(out, exist_ok=True)
S = 600
for k in range(0, len(paths), 4):
    c = Image.new('RGB', (2*S + 6, 2*S + 6), (0, 0, 0))
    for n, p in enumerate(paths[k:k+4]):
        im = Image.open(p).convert('RGB').resize((S, S), Image.LANCZOS)
        d = ImageDraw.Draw(im); name = os.path.basename(p)[:-4]
        d.rectangle([0, 0, 8 + 6*len(name), 14], fill=(255, 255, 0)); d.text((3, 2), f'{"ABCD"[n]} {name}', fill=(0, 0, 0))
        c.paste(im, ((n % 2)*(S + 6), (n // 2)*(S + 6)))
    f = os.path.join(out, f'm{k//4:03d}.png'); c.save(f); print(f, ' '.join(os.path.basename(p)[:-4] for p in paths[k:k+4]))
