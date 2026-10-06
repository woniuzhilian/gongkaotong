# -*- coding: utf-8 -*-
"""Crop option figures from the PDF and save; used to repair empty-option questions."""
import sys, os, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')

PDF=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
OUT=r"C:\Users\Administrator\.qclaw\workspace\pdfcrop"
os.makedirs(OUT, exist_ok=True)
d=pymupdf.open(PDF)

def page_label_imgs(i):
    page=d[i]
    words=page.get_text("words")
    labels=[(w[0],w[1],w[2],w[3],w[4]) for w in words if re.fullmatch(r'（[A-D]）',w[4])]
    imgs=[im['bbox'] for im in page.get_image_info()]
    return labels, imgs

def crop(pg_index, bbox, name, dpi=300, pad=5):
    page=d[pg_index]
    x0,y0,x1,y1=bbox
    clip=pymupdf.Rect(max(0,x0-pad),max(0,y0-pad),min(page.rect.x1,x1+pad),min(page.rect.y1,y1+pad))
    pix=page.get_pixmap(clip=clip, dpi=dpi)
    fn=os.path.join(OUT,name)
    pix.save(fn)
    return fn

def pick_img(labels, imgs, letter):
    lab=[l for l in labels if l[4]==f'（{letter}）']
    if not lab: return None
    lx0,ly0,lx1,ly1,_=lab[0]
    best=None
    for b in imgs:
        ix0,iy0,ix1,iy1=b
        ov=min(lx1,ix1)-max(lx0,ix0)
        gap=ly0-iy1
        if ov>0 and -10<=gap<=130:
            score=(ov, -abs(gap))
            if best is None or score>best[0]:
                best=(score,b)
    return best[1] if best else None

def option_figs(stem_sub, outprefix):
    pg=None
    for i in range(len(d)):
        if stem_sub in d[i].get_text():
            pg=i; break
    if pg is None:
        print("stem not found", stem_sub); return
    res={}
    for off in (0,1):
        if pg+off>=len(d): break
        labels,imgs=page_label_imgs(pg+off)
        for letter in "ABCD":
            if letter in res: continue
            b=pick_img(labels,imgs,letter)
            if b:
                fn=crop(pg+off,b,f"{outprefix}_{letter}.png")
                res[letter]=fn
    print(outprefix, {k:os.path.basename(v) for k,v in res.items()})
    return res

if __name__=="__main__":
    option_figs("简支梁AB", "q306")
    option_figs("设周期信号U(t)的幅值频谱", "q447")
