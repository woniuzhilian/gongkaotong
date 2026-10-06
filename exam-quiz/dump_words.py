# -*- coding: utf-8 -*-
import sys, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')
p=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d=pymupdf.open(p)
for pg in [147,148]:
    page=d[pg-1]
    print(f"===== page {pg} words =====")
    for w in page.get_text("words"):
        x0,y0,x1,y1,txt=w[0],w[1],w[2],w[3],w[4]
        if re.search(r'[A-D（）()]', txt) or '2016' in txt or '201' in txt:
            print(f"  ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}) {txt!r}")
    print("  --- image bboxes ---")
    for im in page.get_image_info():
        x0,y0,x1,y1=im['bbox']; print(f"  IMG ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
    print("  --- drawings bboxes ---")
    for dr in page.get_drawings():
        r=dr['rect']; print(f"  DRW ({r.x0:.0f},{r.y0:.0f},{r.x1:.0f},{r.y1:.0f}) items={len(dr['items'])}")
