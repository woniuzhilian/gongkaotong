# -*- coding: utf-8 -*-
import sys, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')
p = r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d = pymupdf.open(p)
# build page->text
# find questions of interest
targets = {'2013-2','2013-11','2013-12','2013-94','2016-67','2014-50'}
for i in range(len(d)):
    t = d[i].get_text()
    for key in list(targets):
        if f"【{key}】" in t:
            print(f"########## {key} on page {i+1} ##########")
            # print from marker to next marker
            idx = t.find(f"【{key}】")
            nxt = re.search(r'【\d{4}(?:补)?-\d+】', t[idx+6:])
            end = idx+6+nxt.start() if nxt else len(t)
            print(t[idx:end][:700])
            print()
