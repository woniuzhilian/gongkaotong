# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))

def rects(pg):
    bs=[]
    for d in pg.get_drawings():
        r=d['rect']
        if r.width<4 and r.height<4: continue
        bs.append([r.x0,r.y0,r.x1,r.y1])
    for g in pg.get_images(full=True):
        for r in pg.get_image_rects(g[0]):
            bs.append([r.x0,r.y0,r.x1,r.y1])
    return bs

def merge(bs,tol=12):
    cl=[]
    for a in bs:
        merged=[a[0],a[1],a[2],a[3]]; touched=1
        while touched:
            touched=0; rest=[]
            for b in cl:
                if not (merged[2]<b[0]-tol or b[2]<merged[0]-tol or merged[3]<b[1]-tol or b[3]<merged[1]-tol):
                    merged[0]=min(merged[0],b[0]);merged[1]=min(merged[1],b[1])
                    merged[2]=max(merged[2],b[2]);merged[3]=max(merged[3],b[3]);touched=1
                else:
                    rest.append(b)
            cl=rest
        cl.append(merged)
    return cl

for p in [147,148,150,151,152,153,159,162,163,164,166,167,168,201,202,203,217,218,219,220,221,222,225,226,243,244,245,246,247,128,129,131,143,144,232,233,92,93,94,95,220]:
    pg=pub[p-1]
    cl=merge(rects(pg))
    cl=[c for c in cl if (c[2]-c[0])>8 and (c[3]-c[1])>8]
    cl=[c for c in cl if not(c[2]-c[0]>560 and (c[3]-c[1])<90)]
    cl.sort(key=lambda c:(round(c[1]),c[0]))
    print(f"### p{p}")
    for c in cl:
        print(f"   ({int(c[0])},{int(c[1])},{int(c[2])},{int(c[3])})")
