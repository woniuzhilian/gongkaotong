# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
OUT=r"C:\Users\Administrator\.qclaw\workspace\pages2"; os.makedirs(OUT,exist_ok=True)
jobs=[("pub","公共基础分类版真题详解（13~24）_题目.pdf",[128,147,151,166,218,243,225]),
      ("pro","岩土专业基础历年真题试题册（2024版）.pdf",[36,42,88])]
for tag,f,pages in jobs:
    d=pymupdf.open(os.path.join(D,f))
    for p in pages:
        pix=d[p-1].get_pixmap(dpi=160)
        fn=os.path.join(OUT,f"{tag}_p{p}.png"); pix.save(fn)
        print(fn, pix.width, pix.height)
