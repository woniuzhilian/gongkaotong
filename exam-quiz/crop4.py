# -*- coding: utf-8 -*-
import sys, os, pymupdf
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=r"C:\Users\Administrator\.qclaw\workspace\opt4"; os.makedirs(OUT,exist_ok=True)
Z=3
# id -> {A:(page,x0,y0,x1,y1), ...}
OPT={
 306:{'A':(147,88,638,247,712),'B':(147,320,638,476,712),'C':(148,86,74,231,143),'D':(148,324,74,476,145)},
 784:{'A':(151,104,556,187,646),'B':(151,205,556,285,646),'C':(151,306,556,386,646),'D':(151,407,556,492,646)},
 669:{'A':(166,152,394,224,602),'B':(166,232,394,302,602),'C':(166,303,394,374,602),'D':(166,374,392,445,602)},
 908:{'A':(167,158,300,203,440),'B':(167,213,300,258,440),'C':(167,271,300,319,440),'D':(167,330,300,376,440)},
 693:{'A':(244,100,73,300,207),'B':(244,100,210,300,336),'C':(244,100,340,300,472),'D':(244,100,479,300,600)},
 666:{'A':(151,88,80,283,190),'B':(151,283,80,475,190),'C':(151,88,204,283,272),'D':(151,283,204,475,272)},
 658:{'A':(128,232,548,378,712)},
 904:{'A':(153,90,178,278,296),'B':(153,285,178,460,296),'C':(153,90,238,278,300),'D':(153,285,238,460,300)},
}
for qid,opts in OPT.items():
    imgs=[]
    for L,(p,x0,y0,x1,y1) in opts.items():
        pg=pub[p-1]
        pix=pg.get_pixmap(matrix=pymupdf.Matrix(Z,Z),clip=pymupdf.Rect(x0,y0,x1,y1))
        fn=os.path.join(OUT,f"q{qid}_{L}.png"); pix.save(fn); imgs.append(fn)
    if len(imgs)>1:
        pil=[Image.open(i) for i in imgs]
        W=max(im.width for im in pil); H=sum(im.height for im in pil)+6*(len(pil)-1)
        cv=Image.new("RGB",(W,H),"white"); y=0
        for im in pil: cv.paste(im,(0,y)); y+=im.height+6
        cv.save(os.path.join(OUT,f"mq{qid}.png"))
    print(qid,"ok",list(opts))
