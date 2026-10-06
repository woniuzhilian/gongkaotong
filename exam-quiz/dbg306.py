# -*- coding: utf-8 -*-
import sys, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
d=pymupdf.open(r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf")
MK=re.compile(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】')
page=d[146]
print("rect", page.rect)
for w in page.get_text("words"):
    if '2016' in w[4] or re.search(r'（[A-D]）', w[4]):
        print(f"  ({w[0]:.0f},{w[1]:.0f},{w[2]:.0f},{w[3]:.0f}) {w[4]!r}  matchMK={bool(MK.search(w[4]))}")
