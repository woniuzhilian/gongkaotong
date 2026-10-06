# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\labels2.txt","w",encoding="utf-8")
PAGES=[128,129,143,144,147,148,150,151,152,153,158,159,162,163,164,166,167,168,201,202,214,215,217,218,219,220,221,222,224,225,227,243,244,245,246,247]
pat=re.compile(r"^[（(]?\s*([A-Da-d])\s*[)）]$")
for p in PAGES:
    pg=pub[p-1]; ws=pg.get_text("words")
    hits=[]
    for w in ws:
        t=w[4].strip()
        m=pat.match(t)
        if m:
            hits.append((m.group(1),round(w[0]),round(w[1]),round(w[2]),round(w[3])))
    OUT.write(f"\n### p{p}: {len(hits)} labels\n")
    for h in sorted(hits,key=lambda x:(x[2],x[1])):
        OUT.write(f"   {h}\n")
OUT.close(); print("done")
