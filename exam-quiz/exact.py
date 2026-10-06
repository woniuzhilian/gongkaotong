# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\exact.txt","w",encoding="utf-8")
def block(anchor,after=420):
    for i in range(len(pub)):
        t=pub[i].get_text()
        m=re.search(re.escape(anchor),t)
        if m:
            OUT.write(f"\n############ {anchor}  (p{i+1})\n"+t[m.start():m.start()+after]+"\n")
            return
    OUT.write(f"\n############ {anchor} NOTFOUND\n")
for a in ["【2017-90】","【2018-60】","【2018-81】","【2018-84】","【2019-83】","【2021-1】","【2017-94】","【2019-96】","【2013-95】","【2013-96】","【2019-95】","【2020-96】","【2018-93】"]:
    block(a)
OUT.close(); print("done")
