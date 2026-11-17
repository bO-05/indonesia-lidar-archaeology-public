"""Fetch Esri World Imagery mosaic around lat/lon. Usage: esri.py lat lon zoom out.png [ntiles=3]"""
import sys, math, io, urllib.request
from PIL import Image, ImageDraw
lat, lon, z, out = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
n = int(sys.argv[5]) if len(sys.argv) > 5 else 3
N = 2**z; fx = (lon+180)/360*N; fy = (1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*N
cx, cy = int(fx), int(fy); h = n//2
img = Image.new('RGB', (256*n, 256*n))
for i in range(n):
    for j in range(n):
        u = f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{cy-h+j}/{cx-h+i}'
        d = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read()
        img.paste(Image.open(io.BytesIO(d)).convert('RGB'), (256*i, 256*j))
px, py = (fx-cx+h)*256, (fy-cy+h)*256
dr = ImageDraw.Draw(img); dr.ellipse([px-6, py-6, px+6, py+6], outline=(255, 255, 0), width=2)
mpp = 156543.03*math.cos(math.radians(lat))/N
dr.line([10, 256*n-15, 10+100/mpp, 256*n-15], fill=(255, 255, 255), width=3); dr.text((12, 256*n-30), '100 m', fill=(255, 255, 255))
img.save(out); print(out, f'{mpp:.2f} m/px')
