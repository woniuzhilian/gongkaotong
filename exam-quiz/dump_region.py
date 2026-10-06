# -*- coding: utf-8 -*-
"""Dump stem->next-question region(s) text and image bboxes for target stems."""
import sys, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')
PUB=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d=pymupdf.open(PUB)
QN=re.compile(r'【\d{4}(?:\s?补)?[-\u2013]\d+】')

def region(i, sub):
    page=d[i]; t=page.get_text()
    pos=t.find(sub)
    if pos<0: return None
    nxt=QN.search(t, pos+1)
    end=nxt.start() if nxt else len(t)
    return t[pos:end]

def dump(sub, pfx):
    for i in range(len(d)):
        if sub in d[i].get_text():
            r=region(i,sub)
            print(f"########## {pfx} page{i+1} ##########")
            print(repr(r))
            print("  IMGS:", [(round(im['bbox'][0]),round(im['bbox'][1]),round(im['bbox'][2]),round(im['bbox'][3])) for im in d[i].get_image_info()])
            if i+1<len(d):
                r2=region(i+1, sub)
                print(f"  -- page{i+2} continuation: {repr(d[i+1].get_text()[:300])}")
                print("  IMGS2:", [(round(im['bbox'][0]),round(im['bbox'][1]),round(im['bbox'][2]),round(im['bbox'][3])) for im in d[i+1].get_image_info()])
            return
    print(pfx,"not found")

for sub,pfx in [("四种材料的应力","q658"),("四根细长","q669"),("整块材料","q784"),("挠曲线大致形状","q904"),("抗弯刚度EI相同","q908"),("等效电路为","q1040")]:
    dump(sub,pfx)
