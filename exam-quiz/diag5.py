# -*- coding: utf-8 -*-
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
PATH = r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
qs = json.load(open(PATH, encoding='utf-8'))
byid={q['id']:q for q in qs}
for i in [65,205,268,533,647,760,774,880,1014,1023,1165,1374,158,169,287,1367]:
    q=byid.get(i)
    if not q: continue
    print(f"--- id={i} {q['bigSubject']}/{q['year']} ---")
    for f in ['question','A','B','C','D','analysis']:
        v=str(q.get(f,''))
        if '\\cdotm' in v or True:
            print(f"  {f}: {v[:220]}")
    print()
