# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
OUT=r"C:\Users\Administrator\.qclaw\workspace\pdfpages2"; os.makedirs(OUT,exist_ok=True)
PUB=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d=pymupdf.open(PUB)
pages=[128,143,147,150,151,152,159,162,163,166,167,197,201,203,214,215,218,221,224,225,232,233,235,240,243,244,245,246]
for p in pages:
    pg=d[p-1]
    pix=pg.get_pixmap(dpi=185)
    fn=os.path.join(OUT,f"p{p:03d}.png"); pix.save(fn)
    print(p, pix.width, pix.height, os.path.basename(fn))
