# -*- coding: utf-8 -*-
"""For selected (page,label_y) rows, crop the 4 option figures using cluster bboxes and build sheets."""
import os, pymupdf
from PIL import Image, ImageDraw
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
OUT=r"C:\Users\Administrator\.qclaw\workspace\rows"
os.makedirs(OUT,exist_ok=True)

def clusters(page):
    rs=[]
    for d in page.get_drawings():
        r=d["rect"]
        if r.width<2 or r.height<2: continue
        rs.append([r.x0,r.y0,r.x1,r.y1])
    for im in page.get_images(full=True):
        try:
            b=page.get_image_bbox(im); rs.append([b.x0,b.y0,b.x1,b.y1])
        except: pass
    changed=True
    while changed:
        changed=False; out=[]
        while rs:
            a=rs.pop(); merged=False
            for b in out:
                if not (a[2]<b[0]-4 or a[0]>b[2]+4 or a[3]<b[1]-4 or a[1]>b[3]+4):
                    b[0]=min(b[0],a[0]);b[1]=min(b[1],a[1]);b[2]=max(b[2],a[2]);b[3]=max(b[3],a[3]);merged=True;changed=True;break
            if not merged: out.append(a)
        rs=out
    return [r for r in rs if (r[3]-r[1])>12 and not (r[2]-r[0]>520 and r[3]-r[1]<20)]

JOBS=[
 ("q546",162,335),("q784",150,653),("q1147",158,349),("q908",166,432),
 ("q904",152,271),("q658",127,550),("q1262",142,635),
]
doc=pymupdf.open(PUB)
for name,pg,ly in JOBS:
    page=doc[pg]
    cl=clusters(page)
    cands=[c for c in cl if c[3]<=ly+10 and c[3]>=ly-170]
    cands.sort(key=lambda c:(c[0]))
    bands=[]
    for c in cands:
        bb=(c[0]-4,c[1]-4,c[2]+4,c[3]+2)
        pix=page.get_pixmap(dpi=200,clip=pymupdf.Rect(*bb))
        p="%s\\%s_%d_%d.png"%(OUT,name,round(c[0]),round(c[1]))
        pix.save(p); bands.append(Image.open(p))
    if not bands: 
        print(name,"no cands"); continue
    h=max(b.height for b in bands)+26
    w=sum(b.width for b in bands)+(len(bands)+1)*8
    sheet=Image.new("RGB",(w,h),"white"); d=ImageDraw.Draw(sheet); x=8
    for i,b in enumerate(bands):
        sheet.paste(b,(x,22)); d.text((x,5),chr(65+i),fill="red"); x+=b.width+8
    sheet.save("%s\\%s_sheet.png"%(OUT,name))
    print(name,"n=%d"%len(bands),sheet.size)
doc.close()
