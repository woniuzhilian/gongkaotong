# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=r"C:\Users\Administrator\.qclaw\workspace\crops1"; os.makedirs(OUT,exist_ok=True)
# (tag, page, x0,y0,x1,y1)
JOBS=[
 ("306_A_p147L",147, 85,552,285,712),
 ("306_B_p147R",147, 285,552,478,712),
 ("306_C_p148L",148, 83,71,242,152),
 ("306_D_p148R",148, 318,71,482,152),
 ("666_stem_p150",150,186,523,404,610),
 ("666_optband_p151",151, 85,80,478,192),
 ("784_sq_p151",151, 100,558,492,648),
 ("904_opts_p153",153, 88,180,460,290),
 ("908_cols_p166",166, 150,395,445,600),
]
for tag,p,x0,y0,x1,y1 in JOBS:
    pg=pub[p-1]
    pix=pg.get_pixmap(matrix=pymupdf.Matrix(3,3), clip=pymupdf.Rect(x0,y0,x1,y1))
    pix.save(os.path.join(OUT,tag+".png"))
print("done")
