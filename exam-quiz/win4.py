# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\win4.txt","w",encoding="utf-8")
for anchor in ["【2017-88】","【2017-89】","【2017-90】","【2017-91】","【2017-92】","【2016-67】","【2018-59】","【2018-60】","【2018-67】","【2018-69】","【2018-89】","【2018-91】","【2019-59】","【2019-67】","【2019-70】","【2019-94】","【2020-65】","【2020-94】","【2021-65】","【2021-66】","【2021-69】","【2021-70】","【2022-81】","【2022-91】","【2023-63】","【2023-64】"]:
    found=False
    for i in range(len(pub)):
        t=pub[i].get_text()
        m=re.search(re.escape(anchor),t)
        if m:
            OUT.write(f"\n===== {anchor} p{i+1}\n"+re.sub(r'[ \t]+',' ',t[m.start():m.start()+300])+"\n")
            found=True; break
    if not found: OUT.write(f"\n===== {anchor} NOTFOUND\n")
OUT.close(); print("done")
