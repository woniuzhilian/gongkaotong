# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
ans=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_答案解析.pdf"))
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\ans.txt","w",encoding="utf-8")
def block(anchor,after=500):
    for i in range(len(ans)):
        t=ans[i].get_text()
        m=re.search(re.escape(anchor),t)
        if m:
            OUT.write(f"\n############ {anchor}  (p{i+1})\n"+t[m.start():m.start()+after]+"\n")
            return
    OUT.write(f"\n############ {anchor} NOTFOUND\n")
for a in ["【2017-88】","【2017-89】","【2017-90】","【2017-91】","【2018-59】","【2018-60】","【2018-80】","【2018-81】","【2018-84】","【2019-83】","【2021-1】","【2017-94】","【2019-95】","【2019-96】","【2013-95】","【2020-94】","【2020-96】","【2018-93】"]:
    block(a)
OUT.close(); print("done")
