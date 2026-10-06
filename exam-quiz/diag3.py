# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
PATH = r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
qs = json.load(open(PATH, encoding='utf-8'))
byid = {q['id']: q for q in qs}

def show(i):
    q = byid.get(i)
    if not q: 
        print(f"--- id {i} NOT FOUND ---"); return
    print(f"===== id={q['id']} year={q['year']} big={q['bigSubject']} small={q['smallSubject']} =====")
    for f in ['question','A','B','C','D','answer','analysis']:
        print(f"  {f}: {q.get(f)}")
    print()

for i in [1,2,3,13,30,47,94,306,658,682,1391,1588,1626,1987,1988,2002]:
    show(i)
