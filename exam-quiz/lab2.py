# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
pat=re.compile(r"^[（(]?\s*([A-Da-d])\s*[)）]$")
for p in [201,202,203,225,226,227,232,233,217,148,159,150,143]:
    pg=pub[p-1]; ws=pg.get_text("words")
    hits=[]
    for w in ws:
        t=w[4].strip(); m=pat.match(t)
        if m: hits.append((m.group(1),round(w[0]),round(w[1]),round(w[2]),round(w[3])))
    print(f"### p{p}: {len(hits)}")
    for h in sorted(hits,key=lambda x:(x[2],x[1])): print("   ",h)
