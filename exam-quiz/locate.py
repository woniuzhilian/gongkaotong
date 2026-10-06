# -*- coding: utf-8 -*-
"""Locate option-figure image bboxes for a question stem across PDF pages."""
import sys, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')
p=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d=pymupdf.open(p)

def find_stem(sub):
    for i in range(len(d)):
        t=d[i].get_text()
        pos=t.find(sub)
        if pos>=0:
            return i
    return None

def page_dump(i):
    page=d[i]
    words=page.get_text("words")
    imgs=page.get_image_info()
    return words, imgs

for sub,label in [("简支梁AB","2016-67")]:
    pg=find_stem(sub)
    print("stem page index",pg)
    for k in (pg, pg+1):
        words,imgs=page_dump(k)
        labels=[(w[0],w[1],w[2],w[3],w[4]) for w in words if re.fullmatch(r'（[A-D]）',w[4])]
        print(f"--- page {k+1} labels: {[(round(l[0]),round(l[1]),l[4]) for l in labels]}")
        print(f"    imgs: {[(round(im['bbox'][0]),round(im['bbox'][1]),round(im['bbox'][2]),round(im['bbox'][3])) for im in imgs]}")
