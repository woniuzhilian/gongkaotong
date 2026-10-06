# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\win3.txt","w",encoding="utf-8")
for anchor in ["【2018-80】","【2018-81】","KCL方程","【2019-95】","【2020-96】","【2022","补-96】"]:
    hit=False
    for i in range(len(pub)):
        t=pub[i].get_text()
        m=re.search(re.escape(anchor),t)
        if m:
            OUT.write(f"\n===== {anchor!r} p{i+1}\n"+re.sub(r'[ \t]+',' ',t[max(0,m.start()-40):m.start()+360])+"\n")
            hit=True; break
    if not hit: OUT.write(f"\n===== {anchor!r} NOTFOUND\n")
OUT.close(); print("done")
