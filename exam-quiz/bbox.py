# -*- coding: utf-8 -*-
import sys, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
p=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d=pymupdf.open(p)
for pg in [147,128,166,159,240,245,243,152,167,201,142,246,203]:
    page=d[pg-1]
    info=page.get_image_info()
    print(f"===== page {pg}: {len(info)} images, {len(page.get_drawings())} drawings =====")
    for k,im in enumerate(info):
        x0,y0,x1,y1=im['bbox']
        print(f"  img{k}: bbox=({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}) w={x1-x0:.0f} h={y1-y0:.0f} xref={im.get('xref')}")
