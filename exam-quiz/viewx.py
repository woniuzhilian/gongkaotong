# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=r"C:\Users\Administrator\.qclaw\workspace\viewx"; os.makedirs(OUT,exist_ok=True)
# regions to inspect
J=[("p148_top",148,60,60,520,175),
   ("p147_bot",147,60,540,520,730),
   ("p151_bot",151,80,550,500,660),
   ("p153_top",153,80,70,470,300),
   ("p166_mid",166,140,390,450,610),
   ("p159_mid",159,80,240,480,360),
   ("p244_top",244,80,70,540,610),
   ("p247_bot",247,80,415,500,720),
   ("p246_top",246,220,130,470,265),
   ("p143_mid",143,220,310,375,440),
  ]
for tag,p,x0,y0,x1,y1 in J:
    pix=pub[p-1].get_pixmap(matrix=pymupdf.Matrix(3,3),clip=pymupdf.Rect(x0,y0,x1,y1))
    pix.save(os.path.join(OUT,tag+".png"))
print("done")
