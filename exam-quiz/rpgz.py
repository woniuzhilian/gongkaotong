# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=r"C:\Users\Administrator\.qclaw\workspace\pgz"; os.makedirs(OUT,exist_ok=True)
for p in [128,131,144,147,148,150,151,152,153,158,159,162,163,164,166,201,202,203,217,218,219,225,226,232,233,243,244,245,246,247]:
    pix=pub[p-1].get_pixmap(matrix=pymupdf.Matrix(2,2))
    pix.save(os.path.join(OUT,f"p{p}.png"))
print("done")
