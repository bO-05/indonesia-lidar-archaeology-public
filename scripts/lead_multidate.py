#!/usr/bin/env python3
"""Multi-date chips for a lead: unique Esri Wayback versions (z18, 3x3 tiles) + BIG CTSRT all-years.
usage: lead_multidate.py lat lon outdir [ctsrt_service_regex]"""
import sys, os, json, math, io, re, hashlib, requests, concurrent.futures as cf
from PIL import Image, ImageDraw
lat,lon,out=float(sys.argv[1]),float(sys.argv[2]),sys.argv[3]; rx=sys.argv[4] if len(sys.argv)>4 else '.'
os.makedirs(out,exist_ok=True); S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0'
wb=json.loads(S.get('https://s3-us-west-2.amazonaws.com/config.maptiles.arcgis.com/waybackconfig.json',timeout=30).text)
rel=sorted(wb.items(),key=lambda kv:kv[1]['itemTitle'])
z=18; N=2**z; fx=(lon+180)/360*N; fy=(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*N; cx,cy=int(fx),int(fy)
def chip(k):
    url=wb[k]['itemURL']; im=Image.new('RGB',(768,768)); h=hashlib.md5()
    for i in range(3):
        for j in range(3):
            r=S.get(url.format(level=z,row=cy-1+j,col=cx-1+i),timeout=30)
            if not r.ok or len(r.content)<500: return k,None,None
            h.update(r.content); im.paste(Image.open(io.BytesIO(r.content)).convert('RGB'),(256*i,256*j))
    return k,h.hexdigest(),im
seen={}; res=[]
with cf.ThreadPoolExecutor(8) as ex:
    for k,hh,im in ex.map(chip,[k for k,_ in rel]):
        if hh and hh not in seen:
            seen[hh]=k; d=wb[k]['itemTitle'][-11:-1]; px,py=(fx-cx+1)*256,(fy-cy+1)*256
            ImageDraw.Draw(im).ellipse([px-8,py-8,px+8,py+8],outline=(255,255,0),width=2)
            fn=f"{out}/wayback_{d}.jpg"; im.save(fn); res.append(fn)
print('wayback unique:',res)
# BIG CTSRT
R='https://geoservices.big.go.id/raster/rest/services/IMAGERY'
svcs=[s['name'] for s in S.get(R+'?f=json',timeout=30).json()['services'] if 'CTSRT' in s['name'] and re.search(rx,s['name'])]
h=0.0009; got=[]
for s in svcs:
    try:
        r=S.get(f"{R.rsplit('/IMAGERY',1)[0]}/{s}/ImageServer/exportImage",params=dict(bbox=f"{lon-h},{lat-h},{lon+h},{lat+h}",bboxSR=4326,imageSR=4326,size="600,600",format="jpg",f="image"),timeout=60)
        if r.ok and len(r.content)>15000:
            fn=f"{out}/{s.split('/')[1]}.jpg"; open(fn,'wb').write(r.content); got.append(fn)
    except Exception as e: pass
print('ctsrt:',got)
# contact sheet
fs=res+got; T=256; cols=4; rows=(len(fs)+cols-1)//cols
M=Image.new('RGB',(cols*T,rows*T))
for i,f in enumerate(fs):
    im=Image.open(f).convert('RGB').resize((T,T)); ImageDraw.Draw(im).text((3,3),os.path.basename(f)[:-4][-22:],fill=(255,255,0)); M.paste(im,((i%cols)*T,(i//cols)*T))
M.save(f"{out}/multidate_sheet.jpg")
