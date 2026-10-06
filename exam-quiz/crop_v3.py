# -*- coding: utf-8 -*-
"""Crop option sub-figures (figures) for the broken questions, build contact sheets."""
import os, pymupdf
from PIL import Image, ImageDraw
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
OUT=r"C:\Users\Administrator\.qclaw\workspace\crops_v3"
CS=r"C:\Users\Administrator\.qclaw\workspace\csheets"
os.makedirs(OUT,exist_ok=True); os.makedirs(CS,exist_ok=True)

# id -> (page0, {letter:(x0,y0,x1,y1)})
JOBS={
 306:(146,{"A":(88,646,244,714),"B":(321,646,473,714),
           "C":(85,72,229,150),"D":(323,72,477,150)}),
 546:(162,{"A":(88,246,188,362),"B":(184,246,282,362),
           "C":(278,246,376,362),"D":(372,246,470,362)}),
 666:(150,{"A":(88,104,277,208),"B":(290,104,477,208),
           "C":(88,206,277,278),"D":(290,206,477,278)}),
 784:(150,{"A":(99,584,163,650),"B":(200,584,266,650),
           "C":(301,584,367,650),"D":(402,584,469,650)}),
 904:(152,{"A":(88,176,272,236),"B":(292,176,472,236),
           "C":(88,235,272,294),"D":(292,235,472,294)}),
 908:(166,{"A":(148,393,220,607),"B":(228,393,302,607),
           "C":(300,393,374,607),"D":(372,393,444,607)}),
 1147:(158,{"A":(90,396,202,516),"B":(202,396,314,516),
            "C":(314,396,426,516),"D":(426,396,538,516)}),
}
def crop(doc,qid,letter,pg,bb,save=True):
    pix=doc[pg].get_pixmap(dpi=200,clip=pymupdf.Rect(*bb))
    path=os.path.join(OUT,"q%d_%s.png"%(qid,letter))
    if save: pix.save(path)
    im=Image.open(path) if save else Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
    return im

doc=pymupdf.open(PUB)
for qid,(pg,letters) in JOBS.items():
    ims=[]
    for L in "ABCD":
        im=crop(doc,qid,L,pg,letters[L])
        ims.append((L,im))
    # contact sheet: A B C D in a row
    h=max(i.height for _,i in ims)+30
    w=sum(i.width for _,i in ims)+ (len(ims)+1)*10
    sheet=Image.new("RGB",(w,h),"white")
    d=ImageDraw.Draw(sheet); x=10
    for L,im in ims:
        sheet.paste(im,(x,25)); d.text((x,5),L,fill="red"); x+=im.width+10
    sheet.save(os.path.join(CS,"q%d_sheet.png"%qid))
    print("q%d sheet %dx%d"%(qid,sheet.width,sheet.height))
doc.close()
