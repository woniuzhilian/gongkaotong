# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\clusters.txt","w",encoding="utf-8")
PAGES=[128,143,144,147,148,150,151,152,153,163,164,166,167,168,201,202,214,215,219,221,222,224,225,243,244,245,246,247]
def boxes(pg):
    bs=[]
    for d in pg.get_drawings():
        r=d['rect']
        if r.width<2 and r.height<2: continue
        bs.append((r.x0,r.y0,r.x1,r.y1))
    for g in pg.get_images(full=True):
        for r in pg.get_image_rects(g[0]):
            bs.append((r.x0,r.y0,r.x1,r.y1))
    return bs
def cluster(bs, gx=12, gy=12):
    bs=[list(b) for b in bs]; changed=True
    while changed:
        changed=False
        out=[]
        while bs:
            a=bs.pop()
            merged=False
            for b in out:
                if not (a[2]<b[0]-gx or b[2]<a[0]-gx or a[3]<b[1]-gy or b[3]<a[1]-gy):
                    b[0]=min(b[0],a[0]); b[1]=min(b[1],a[1]); b[2]=max(b[2],a[2]); b[3]=max(b[3],a[3])
                    merged=True; changed=True; break
            if not merged: out.append(a)
        bs=out
    return sorted(bs,key=lambda b:(round(b[1]),b[0]))
for p in PAGES:
    pg=pub[p-1]
    cs=cluster(boxes(pg))
    OUT.write(f"\n### p{p}: {len(cs)} clusters\n")
    for c in cs:
        if (c[2]-c[0])<8 and (c[3]-c[1])<8: continue
        OUT.write(f"   ({c[0]:.0f},{c[1]:.0f},{c[2]:.0f},{c[3]:.0f})  w={c[2]-c[0]:.0f} h={c[3]-c[1]:.0f}\n")
OUT.close(); print("done")
