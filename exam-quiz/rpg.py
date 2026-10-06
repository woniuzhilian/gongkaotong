# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=r"C:\Users\Administrator\.qclaw\workspace\pg"; os.makedirs(OUT,exist_ok=True)
PAGES=[143,144,147,148,150,151,152,153,163,164,166,167,168,201,202,214,215,219,221,222,224,225,227,243,244,245,246,247]
for p in PAGES:
    pg=pub[p-1]
    pix=pg.get_pixmap(matrix=pymupdf.Matrix(2,2))
    fn=os.path.join(OUT,f"p{p}.png"); pix.save(fn)
    print(p, pix.width, pix.height)
