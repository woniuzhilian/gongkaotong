# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=r"C:\Users\Administrator\.qclaw\workspace\optcrop2"; os.makedirs(OUT,exist_ok=True)
# id: list of (page, x0,y0,x1,y1)
CROPS={
 666:[(151,88,80,475,272)],
 784:[(151,104,558,492,672)],
 669:[(167,158,303,378,448)],
 908:[(167,153,398,442,602)],
 693:[(244,112,73,292,602)],
 904:[(153,88,176,458,272)],
 658:[(128,236,552,374,712)],
 306:[(147,85,640,478,714),(148,85,70,478,148)],
 1040:[(201,86,591,382,700),(202,86,73,382,196)],
}
Z=3
for qid,crops in CROPS.items():
    imgs=[]
    for (p,x0,y0,x1,y1) in crops:
        pg=pub[p-1]
        pix=pg.get_pixmap(matrix=pymupdf.Matrix(Z,Z),clip=pymupdf.Rect(x0,y0,x1,y1))
        tmp=os.path.join(OUT,f"_tmp{qid}_{p}.png"); pix.save(tmp); imgs.append(tmp)
    if len(imgs)==1:
        os.replace(imgs[0],os.path.join(OUT,f"q{qid}.png"))
    else:
        from PIL import Image
        pil=[Image.open(i) for i in imgs]
        W=max(im.width for im in pil); H=sum(im.height for im in pil)+8*(len(pil)-1)
        canvas=Image.new("RGB",(W,H),"white"); y=0
        for im in pil:
            canvas.paste(im,(0,y)); y+=im.height+8
        canvas.save(os.path.join(OUT,f"q{qid}.png"))
        for i in imgs: os.remove(i)
    print(qid,"ok")
