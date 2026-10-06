# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=r"C:\Users\Administrator\.qclaw\workspace\pg7"; os.makedirs(OUT,exist_ok=True)
for p in [147,148,150,245,246,247,203]:
    pix=pub[p-1].get_pixmap(matrix=pymupdf.Matrix(2,2))
    pix.save(os.path.join(OUT,f"p{p}.png"))
print("done")
