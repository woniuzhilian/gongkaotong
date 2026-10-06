# -*- coding: utf-8 -*-
import sys, re, pymupdf, json
sys.stdout.reconfigure(encoding='utf-8')
PUB=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d=pymupdf.open(PUB)
LBL=re.compile(r'[（(]([A-D])[）)]')
Q={q['id']:q for q in json.load(open(r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json",encoding='utf-8'))}
for qid,pg in [(447,218),(448,218),(669,166),(693,243),(784,151),(908,167),(1160,203)]:
    q=Q[qid]
    for p in (pg,pg+1):
        page=d[p-1]
        labs=[(w[4],round(w[0]),round(w[1])) for w in page.get_text("words") if LBL.search(w[4])]
        print(f"id{qid} p{p}: {labs}")
    print()
