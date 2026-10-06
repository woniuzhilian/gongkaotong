# -*- coding: utf-8 -*-
import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')
P=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
Q=json.load(open(P,encoding='utf-8'))
byid={q['id']:q for q in Q}
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002]
def hasimg(s): return bool(re.search(r"<img",s or ""))
for i in IDS:
    q=byid[i]
    print(f"id{i} {q.get('year')}-{q.get('yearQnum')} ans={q.get('answer')} Aimg={hasimg(q.get('A'))} B='{(q.get('B') or '')[:20]}'")
    print(f"   Q: {(q.get('question') or '')[:90]}")
    print(f"   A: {(q.get('A') or '')[:110]}")
