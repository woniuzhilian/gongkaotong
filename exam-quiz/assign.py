# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
pat=re.compile(r"^[（(]?\s*([A-Da-d])\s*[)）]$")
def boxes(pg):
    bs=[]
    for d in pg.get_drawings():
        r=d['rect']
        if r.width<3 and r.height<3: continue
        if r.width>560 and r.height<200: continue
        bs.append([r.x0,r.y0,r.x1,r.y1])
    for g in pg.get_images(full=True):
        for r in pg.get_image_rects(g[0]):
            if r.width>560 and r.height<200: continue
            bs.append([r.x0,r.y0,r.x1,r.y1])
    return bs
def cluster(bs, gx=14, gy=14):
    changed=True
    while changed:
        changed=False; out=[]
        for a in bs:
            hit=None
            for b in out:
                if not (a[2]<b[0]-gx or b[2]<a[0]-gx or a[3]<b[1]-gy or b[3]<a[1]-gy):
                    hit=b; break
            if hit:
                hit[0]=min(hit[0],a[0]);hit[1]=min(hit[1],a[1]);hit[2]=max(hit[2],a[2]);hit[3]=max(hit[3],a[3]);changed=True
            else: out.append(list(a))
        bs=out
    return [c for c in bs if not(c[2]-c[0]<10 and c[3]-c[1]<10)]
PAGES=[128,147,148,159,162,164,166,201,202,219,233,244,245,247,131,143,144,150,151,152,153,203,226,225,217,218,232]
for p in PAGES:
    pg=pub[p-1]; cs=cluster(boxes(pg))
    print(f"### p{p} ({len(cs)})")
    for c in sorted(cs,key=lambda b:(round(b[1]),b[0])):
        print(f"   ({c[0]:.0f},{c[1]:.0f},{c[2]:.0f},{c[3]:.0f}) w={c[2]-c[0]:.0f} h={c[3]-c[1]:.0f}")
    labs=[]
    for w in pg.get_text("words"):
        m=pat.match(w[4].strip())
        if m: labs.append((m.group(1),round(w[0]),round(w[1]),round(w[2]),round(w[3])))
    print("   L:",sorted(labs,key=lambda x:(x[2],x[1])))
