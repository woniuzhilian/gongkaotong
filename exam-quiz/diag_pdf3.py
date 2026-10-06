# -*- coding: utf-8 -*-
import sys, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')
p = r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d = pymupdf.open(p)
# collect all 【year-num】 markers
markers=[]
for i in range(len(d)):
    t = d[i].get_text()
    for m in re.finditer(r'【(\d{4}(?:补)?)-(\d+)】', t):
        markers.append((i+1, m.group(1), m.group(2)))
print("total question markers:", len(markers))
print("first 15:", markers[:15])
print("last 5:", markers[-5:])
# years distribution
import collections
print(collections.Counter(y for _,y,_ in markers))
# Answer pdf markers
pa = r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_答案解析.pdf"
da = pymupdf.open(pa)
am=[]
for i in range(len(da)):
    t = da[i].get_text()
    for m in re.finditer(r'【(\d{4}(?:补)?)-(\d+)】', t):
        am.append((i+1, m.group(1), m.group(2)))
print("\nanswer markers:", len(am), collections.Counter(y for _,y,_ in am))
print("first 10:", am[:10])
