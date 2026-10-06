# -*- coding: utf-8 -*-
import sys, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
p=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d=pymupdf.open(p)
out=r"C:\Users\Administrator\.qclaw\workspace\pdfpages"
import os; os.makedirs(out, exist_ok=True)
for pg in [147,128,166]:
    page=d[pg-1]
    pix=page.get_pixmap(dpi=160)
    fn=os.path.join(out, f"pub_p{pg}.png")
    pix.save(fn)
    print("saved", fn, pix.width, pix.height)
