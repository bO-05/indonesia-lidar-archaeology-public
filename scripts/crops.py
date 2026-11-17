"""Make zoom crops (200 m) around candidate points, then contact sheets.
Usage: python crops.py candidates.csv outdir   (csv columns: id,src,px,py)"""
import sys, csv, os, numpy as np, rasterio
from rasterio.windows import Window
from scipy import ndimage
from PIL import Image, ImageDraw
cand, outdir = sys.argv[1:3]; os.makedirs(outdir, exist_ok=True)
R = 100
def render(a):
    v = (a > -1e30) & (a < 1e5); a = np.where(v, a, np.median(a[v]))
    hs = 0
    for az in (315, 45, 135, 225):
        gy, gx = np.gradient(a * 3)
        sl = np.pi/2 - np.arctan(np.hypot(gx, gy)); asp = np.arctan2(-gx, gy)
        hs = hs + np.sin(np.radians(35))*np.sin(sl) + np.cos(np.radians(35))*np.cos(sl)*np.cos(np.radians(az)-asp)
    hs = (hs - hs.min()) / (np.ptp(hs) + 1e-6)
    l = np.clip((a - ndimage.uniform_filter(a, 41)) / 1.5, -1, 1)
    rgb = np.stack([hs*0.65 + np.clip(l, 0, 1)*0.35, hs*0.65, hs*0.65 + np.clip(-l, 0, 1)*0.35], -1)
    return (np.clip(rgb, 0, 1)*255).astype(np.uint8), float(np.ptp(a))
ims = []
for row in csv.DictReader(open(cand)):
    with rasterio.open(f"data/jambi/DTM_{row['src']}.tif") as r:
        px, py = int(row['px']), int(row['py'])
        w = Window(max(0, px-R), max(0, py-R), 2*R, 2*R)
        a = r.read(1, window=w, boundless=True, fill_value=-3.4e38).astype(np.float32)
    rgb, rng = render(a)
    im = Image.fromarray(rgb).resize((400, 400), Image.LANCZOS)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 400, 16], fill=(255, 255, 255))
    d.text((3, 2), f"{row['id']} relief{rng:.1f}m", fill=(0, 0, 0))
    d.rectangle([10, 385, 10+100, 390], fill=(0, 0, 0))  # 50 m bar
    im.save(f"{outdir}/{row['id']}.png"); ims.append(im)
for s in range(0, len(ims), 9):
    sheet = Image.new('RGB', (1200, 1200), 'white')
    for k, im in enumerate(ims[s:s+9]):
        sheet.paste(im, ((k % 3)*400, (k//3)*400))
    sheet.save(f"{outdir}/sheet_{s//9:02d}.png")
print(len(ims))
