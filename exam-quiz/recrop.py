# -*- coding: utf-8 -*-
import sys, os, pymupdf
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=r"C:\Users\Administrator\.qclaw\workspace\final"; Z=3
OPT={
 666:{'A':(151,104,560,185,650),'B':(151,205,560,282,650),'C':(151,306,560,383,650),'D':(151,407,560,489,650)},
 904:{'A':(153,88,182,255,224),'B':(153,292,182,460,224),'C':(153,88,240,255,272),'D':(153,292,240,460,272)},
 908:{'A':(167,180,256,285,362),'B':(167,296,256,410,362),'C':(167,206,432,300,600),'D':(167,300,432,395,600)},
 1262:{'A':(144,86,66,180,162),'B':(144,180,66,274,162),'C':(144,276,66,372,162),'D':(144,372,66,478,162)},
}
for qid,opts in OPT.items():
    ims=[]
    for L in 'ABCD':
        p,x0,y0,x1,y1=opts[L]
        pix=pub[p-1].get_pixmap(matrix=pymupdf.Matrix(Z,Z),clip=pymupdf.Rect(x0,y0,x1,y1))
        fn=os.path.join(OUT,f'x{qid}_{L}.png'); pix.save(fn); ims.append(fn)
    pil=[Image.open(i) for i in ims]
    W=max(i.width for i in pil); H=sum(i.height for i in pil)+18
    cv=Image.new('RGB',(W,H),'white'); y=0
    for i in pil: cv.paste(i,(0,y)); y+=i.height+6
    cv.save(os.path.join(OUT,f'n{qid}.png'))
print('ok')
