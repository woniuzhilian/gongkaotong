# -*- coding: utf-8 -*-
import sys, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')
p = r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d = pymupdf.open(p)
targets=['2016-67','2017-88','2019-59','2019-67','2019-70','2021-89']
for i in range(len(d)):
    t=d[i].get_text()
    for key in list(targets):
        if f"【{key}】" in t:
            idx=t.find(f"【{key}】")
            nxt=re.search(r'【\d{4}(?:补)?-\d+】', t[idx+6:])
            end=idx+6+nxt.start() if nxt else len(t)
            print(f"########## {key} page {i+1} ##########")
            print(t[idx:end][:500])
            # count images on page
            imgs=d[i].get_images(full=True)
            print(f"  [page has {len(imgs)} embedded images]")
            print()
