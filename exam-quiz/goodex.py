# -*- coding: utf-8 -*-
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
P=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
Q=json.load(open(P,encoding='utf-8'))
byid={q['id']:q for q in Q}
for i in [90,92,183,210,330,425,450,690,799,810,1028]:
    q=byid[i]
    print(f"===== id{i} {q['year']}-{q.get('yearQnum')} =====")
    print("Q:",(q['question'] or '')[:160])
    for k in "ABCD":
        print(f"  {k}:",(q[k] or '')[:150])
    print("  ans:",q['answer'])
