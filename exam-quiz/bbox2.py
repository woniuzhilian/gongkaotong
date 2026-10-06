# -*- coding: utf-8 -*-
import sys, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
p=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d=pymupdf.open(p)
for pg in [146,147,148,149,128,129,165,166,167,168]:
    page=d[pg-1]
    info=page.get_image_info()
    t=page.get_text().replace('\n',' ')
    print(f"===== page {pg}: {len(info)} imgs, {len(page.get_drawings())} drawings =====")
    print("  text head:", t[:90])
    for k,im in enumerate(info):
        x0,y0,x1,y1=im['bbox']
        print(f"    img{k}: ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}) {x1-x0:.0f}x{y1-y0:.0f}")
