# -*- coding: utf-8 -*-
"""Crop option figures WITH their （X） label included, for empty-option questions."""
import sys, os, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')
PUB=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
OUT=r"C:\Users\Administrator\.qclaw\workspace\pdfcrop2"
os.makedirs(OUT, exist_ok=True)
d=pymupdf.open(PUB)

def page_objs(i):
    page=d[i]
    words=page.get_text("words")
    labels=[(w[0],w[1],w[2],w[3],w[4]) for w in words if re.fullmatch(r'（[A-D]）',w[4])]
    imgs=[im['bbox'] for im in page.get_image_info()]
    return labels, imgs

def crop_union(pg, bboxes, name, dpi=300, pad=6):
    page=d[pg]
    x0=min(b[0] for b in bboxes)-pad; y0=min(b[1] for b in bboxes)-pad
    x1=max(b[2] for b in bboxes)+pad; y1=max(b[3] for b in bboxes)+pad
    clip=pymupdf.Rect(max(0,x0),max(0,y0),min(page.rect.x1,x1),min(page.rect.y1,y1))
    pix=page.get_pixmap(clip=clip, dpi=dpi)
    fn=os.path.join(OUT,name); pix.save(fn); return fn

def figs(stem_sub, prefix):
    pg=None
    for i in range(len(d)):
        if stem_sub in d[i].get_text(): pg=i; break
    if pg is None: print(prefix,"stem not found"); return
    res={}
    for off in (0,1):
        if pg+off>=len(d): break
        labels,imgs=page_objs(pg+off)
        for letter in "ABCD":
            if letter in res: continue
            lab=[l for l in labels if l[4]==f'（{letter}）']
            if not lab: continue
            lx0,ly0,lx1,ly1,_=lab[0]
            best=None
            for b in imgs:
                ov=min(lx1,b[2])-max(lx0,b[0]); gap=ly0-b[3]
                if ov>0 and -10<=gap<=140:
                    sc=(ov,-abs(gap))
                    if best is None or sc>best[0]: best=(sc,b)
            if best:
                res[letter]=crop_union(pg+off,[best[1],(lx0,ly0,lx1,ly1)],f"{prefix}_{letter}.png")
    print(prefix, sorted(res.keys()))

for sub,pfx in [("简支梁AB","q306"),("四种材料的应力","q658"),("四根细长","q669"),("整块材料","q784"),("挠曲线大致形状","q904"),("抗弯刚度EI相同","q908"),("等效电路为","q1040"),("平面应力状态","q1147"),("等效电流源模型","q1160"),("静矩","q1262"),("小信号模型","q1292"),("能够完成加法运算","q693")]:
    figs(sub,pfx)
