# -*- coding: utf-8 -*-
import pymupdf, io, os
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
PROQ=BASE+r"\岩土专业基础分类真题解析（16~24）_题目.pdf"

def clusters(page):
    rs=[]
    for d in page.get_drawings():
        r=d["rect"]
        if r.width<1 or r.height<1: continue
        rs.append([r.x0,r.y0,r.x1,r.y1])
    for im in page.get_images(full=True):
        try:
            b=page.get_image_bbox(im)
            rs.append([b.x0,b.y0,b.x1,b.y1])
        except: pass
    # merge
    changed=True
    while changed:
        changed=False
        out=[]
        while rs:
            a=rs.pop()
            merged=False
            for b in out:
                if not (a[2]<b[0]-6 or a[0]>b[2]+6 or a[3]<b[1]-6 or a[1]>b[3]+6):
                    b[0]=min(b[0],a[0]);b[1]=min(b[1],a[1]);b[2]=max(b[2],a[2]);b[3]=max(b[3],a[3])
                    merged=True;changed=True;break
            if not merged: out.append(a)
        rs=out
    # drop header/footer wide thin
    res=[r for r in rs if not (r[3]-r[1]<8) and not (r[2]-r[0]>520 and r[3]-r[1]<20)]
    res.sort(key=lambda r:(round(r[1]),round(r[0])))
    return [[round(v,1) for v in r] for r in res]

PAGES={"pub":[127,143,146,147,150,151,152,153,158,159,166,200,201,203,213,219,221,223,242,243,244,245,246,247],
       "pro":[35,36,42,88,89]}
out=[]
for k,pp in PAGES.items():
    path=PUBQ if k=="pub" else PROQ
    doc=pymupdf.open(path)
    for p in pp:
        if p>=doc.page_count: continue
        cl=clusters(doc[p])
        out.append("== %s p=%d =="%(k,p))
        for c in cl: out.append("   %s"%c)
    doc.close()
io.open(r"C:\Users\Administrator\.qclaw\workspace\clusters_v2.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
