# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=r"C:\Users\Administrator\.qclaw\workspace\optcrop3"; os.makedirs(OUT,exist_ok=True)
# corrected: id -> list of (page,x0,y0,x1,y1)
CROPS={
 669:[(166,150,392,440,608)],
 908:[(167,155,300,395,452)],
 904:[(153,148,166,420,292)],
 1040:[(201,86,588,382,712),(202,86,68,382,202)],
}
Z=3
from PIL import Image
for qid,crops in CROPS.items():
    imgs=[]
    for (p,x0,y0,x1,y1) in crops:
        pg=pub[p-1]
        pix=pg.get_pixmap(matrix=pymupdf.Matrix(Z,Z),clip=pymupdf.Rect(x0,y0,x1,y1))
        tmp=os.path.join(OUT,f"_t{qid}_{p}.png"); pix.save(tmp); imgs.append(tmp)
    if len(imgs)==1:
        os.replace(imgs[0],os.path.join(OUT,f"q{qid}.png"))
    else:
        pil=[Image.open(i) for i in imgs]
        W=max(im.width for im in pil); H=sum(im.height for im in pil)+8*(len(pil)-1)
        canvas=Image.new("RGB",(W,H),"white"); y=0
        for im in pil: canvas.paste(im,(0,y)); y+=im.height+8
        canvas.save(os.path.join(OUT,f"q{qid}.png"))
        for i in imgs: os.remove(i)
    print(qid,"ok")
