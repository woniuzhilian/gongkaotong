# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=r"C:\Users\Administrator\.qclaw\workspace\zoom"; os.makedirs(OUT,exist_ok=True)
REG=[
 (151,70,70,475,280,"p151_666"),
 (153,90,150,470,310,"p153_904"),
 (201,82,80,395,720,"p201_1040a"),
 (202,80,78,390,210,"p202_1040b"),
 (144,70,60,490,165,"p144_1262"),
 (167,155,150,450,300,"p167_908"),
]
Z=4
for (p,x0,y0,x1,y1,name) in REG:
    pg=pub[p-1]
    pix=pg.get_pixmap(matrix=pymupdf.Matrix(Z,Z),clip=pymupdf.Rect(x0,y0,x1,y1))
    pix.save(os.path.join(OUT,f"{name}.png")); print(name,pix.width,pix.height)
