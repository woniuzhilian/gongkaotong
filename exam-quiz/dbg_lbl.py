# -*- coding: utf-8 -*-
import sys, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
PUB=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d=pymupdf.open(PUB)
page=d[146]  # p147
t=page.get_text()
print("has （A）", '（A）' in t, "has (A)", '(A)' in t)
for w in page.get_text("words"):
    if 'A' in w[4] or 'B' in w[4]:
        print(repr(w[4]), f"{w[0]:.0f},{w[1]:.0f}")
print("---- around")
i=t.find('（A）')
print(repr(t[i-30:i+80]))
