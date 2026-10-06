# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
targets=["【2021-89】","【2021-90】","【2021-91】","【2021-92】","【2021-93】","【2021-94】","【2022-89】","【2022-90】","【2022-91】","【2022-92】","【2022-93】","【2022-94】","【2023-93】","【2023-94】","【2022 补-89】","【2022 补-90】","【2022 补-91】","【2022 补-92】","【2022 补-93】"]
for t in targets:
    hits=[p+1 for p in range(len(pub)) if pub[p].search_for(t)]
    print(t, hits)
