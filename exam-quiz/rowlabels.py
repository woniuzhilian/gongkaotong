# -*- coding: utf-8 -*-
"""Auto-locate (A)(B)(C)(D) option-label rows per page and crop the figure band above each."""
import os, re, pymupdf
from PIL import Image, ImageDraw
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
OUT=r"C:\Users\Administrator\.qclaw\workspace\rows"
os.makedirs(OUT,exist_ok=True)
PAGES=[127,142,143,144,146,147,150,151,152,153,158,159,162,163,164,165,166,167,168,200,201,202,203,213,219,221,223,242,243,244,245,246,247]
LBL=re.compile(r'^[（(]?([ABCD])[）)]?$')

def label_rows(page):
    words=page.get_text("words")  # x0,y0,x1,y1,word,...
    rows={}
    for w in words:
        m=LBL.match(w[4].strip())
        if m:
            y=round(w[1],0)
            rows.setdefault(y,[]).append((m.group(1),w[0],w[2]))
    # merge rows within 6pt
    merged={}
    for y in sorted(rows):
        for my in list(merged):
            if abs(my-y)<=8:
                merged[my].extend(rows[y]); break
        else:
            merged[y]=list(rows[y])
    out={}
    for y,items in merged.items():
        letters=sorted(set(i[0] for i in items))
        if len(letters)>=2:
            out[y]=items
    return out

doc=pymupdf.open(PUB)
report=[]
for pg in PAGES:
    if pg>=doc.page_count: continue
    page=doc[pg]
    rows=label_rows(page)
    report.append("== p%d =="%pg)
    for y,items in sorted(rows.items()):
        items=sorted(items,key=lambda t:t[1])
        desc=" ".join("%s@%.0f"%(l,x0) for l,x0,x1 in items)
        report.append("  y=%.0f : %s"%(y,desc))
doc.close()
open(r"C:\Users\Administrator\.qclaw\workspace\rows_report.txt","w",encoding="utf-8").write("\n".join(report))
print("ok")
