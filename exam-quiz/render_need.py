# -*- coding: utf-8 -*-
import os
import pymupdf

BASE = r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ = os.path.join(BASE, "公共基础分类版真题详解（13~24）_题目.pdf")
PROQ = os.path.join(BASE, "岩土专业基础分类真题解析（16~24）_题目.pdf")
OUT = r"C:\Users\Administrator\.qclaw\workspace\pgs"
os.makedirs(OUT, exist_ok=True)

pub_pages=[126,127,128,129,146,147,148,149,150,151,152,153,158,159,161,162,163,164,165,166,
           200,201,202,203,223,224,225,231,232,233,242,243,244,245,246]
pro_pages=[35,36,41,42,87,88,89]

doc=pymupdf.open(PUBQ)
for p in pub_pages:
    if p < doc.page_count:
        pix=doc[p].get_pixmap(dpi=200)
        pix.save(os.path.join(OUT,"pub_p%03d.png"%p))
doc.close()

doc=pymupdf.open(PROQ)
for p in pro_pages:
    if p < doc.page_count:
        pix=doc[p].get_pixmap(dpi=200)
        pix.save(os.path.join(OUT,"pro_p%03d.png"%p))
doc.close()
print("rendered", len(os.listdir(OUT)))
