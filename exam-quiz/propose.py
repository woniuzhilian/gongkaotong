# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
pat=re.compile(r"^[（(]?\s*([A-Da-d])\s*[)）]$")

def clusters(pg):
    bs=[]
    for d in pg.get_drawings():
        r=d['rect']
        if r.width<3 and r.height<3: continue
        bs.append([r.x0,r.y0,r.x1,r.y1])
    for g in pg.get_images(full=True):
        for r in pg.get_image_rects(g[0]):
            bs.append([r.x0,r.y0,r.x1,r.y1])
    # merge
    out=[]
    while bs:
        a=bs.pop(); merged=True
        while merged:
            merged=False
            for b in out:
                if not (a[2]<b[0]-14 or b[2]<a[0]-14 or a[3]<b[1]-14 or b[3]<a[1]-14):
                    b[0]=min(b[0],a[0]);b[1]=min(b[1],a[1]);b[2]=max(b[2],a[2]);b[3]=max(b[3],a[3])
                    out.remove(b); bs.append(a); merged=True; break
        out.append(a)
    # drop header/footer
    out=[c for c in out if not(c[2]-c[0]>580 and (c[3]-c[1]<80 or c[1]<60))]
    return out

def rows_of(labs, tol=18):
    labs=sorted(labs,key=lambda x:(x[1],x[0]))
    rows=[]
    for l in labs:
        placed=False
        for r in rows:
            if abs(r[0][1]-l[1])<=tol: r.append(l); placed=True; break
        if not placed: rows.append([l])
    for r in rows: r.sort(key=lambda x:x[1])
    return rows

PAGES=[128,147,148,150,151,153,159,162,163,164,166,201,202,217,218,219,225,226,233,243,244,245,246,247,131,152,203]
for p in PAGES:
    pg=pub[p-1]; labs=[]
    for w in pg.get_text("words"):
        m=pat.match(w[4].strip())
        if m: labs.append((m.group(1),round(w[0],1),round(w[1],1),round(w[2],1),round(w[3],1)))
    if not labs: 
        print(f"### p{p}: NO LABELS"); continue
    cs=clusters(pg)
    rows=rows_of(labs)
    print(f"### p{p}")
    for r in rows:
        xs=[l[1] for l in r]
        over=[c for c in cs if c[0]< max(xs)+120 and c[2]> min(xs)-120]
        print(f"   row y={r[0][2]:.0f} labels={[ (l[0],int(l[1]),int(l[2])) for l in r]}")
        print(f"      clusters={[ (int(c[0]),int(c[1]),int(c[2]),int(c[3])) for c in sorted(over,key=lambda c:c[1])]}")
