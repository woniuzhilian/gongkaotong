# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题解析（13~24）_题目.pdf")) if False else pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=r"C:\Users\Administrator\.qclaw\workspace\bands2"; os.makedirs(OUT,exist_ok=True)
J=[("306_p147",147,75,535,500,730),
   ("306_p148",148,75,55,500,175),
   ("666_p150",150,140,510,460,615),
   ("904_p153",153,80,70,470,300),
   ("908_p167",167,150,290,420,450),
   ("1040_p201",201,80,440,420,710),
   ("1040_p202",202,240,260,360,420),
   ("784_p151",151,80,550,500,665),
   ("812_p159",159,80,235,480,365),
   ("1262_p143",143,220,300,375,445),
   ("1262_p144",144,100,60,520,180),
   ("2002_p246",246,220,130,470,270),
   ("1292_p247",247,80,410,500,730),
   ("1626x_",1626,0,0,0,0),
  ]
for tag,p,x0,y0,x1,y1 in J:
    if tag.endswith("x_"): continue
    pix=pub[p-1].get_pixmap(matrix=pymupdf.Matrix(3,3),clip=pymupdf.Rect(x0,y0,x1,y1))
    pix.save(os.path.join(OUT,tag+".png"))
print("done")
