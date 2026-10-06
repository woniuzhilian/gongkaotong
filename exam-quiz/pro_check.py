# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
PRO=r"E:\应用程序开发\刷题\题目和答案pdf\岩土专业基础历年真题试题册（2024版）.pdf"
d=pymupdf.open(PRO)
print("pages", len(d))
# marker formats across pages
pats={}
for i in range(len(d)):
    t=d[i].get_text()
    for m in re.finditer(r'[【\[]?\s*(\d{4})\s*[-–]\s*(\d{1,3})', t):
        pats.setdefault(m.group(0)[:12],0)
print("sample numeric markers:", list(pats.keys())[:30])
# show a page around 36
for p in (36,42,50,51,81,88):
    t=d[p-1].get_text()
    print(f"----- PRO p{p} len={len(t)} -----")
    print(t[:400].replace("\n"," | "))
