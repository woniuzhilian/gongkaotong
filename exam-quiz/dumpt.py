# -*- coding: utf-8 -*-
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
P=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
data=json.load(open(P,encoding='utf-8'))
ids=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002]
for q in data:
    if q['id'] in ids:
        print(f"### id={q['id']} year={q['year']} yq={q['yearQnum']} sub={q.get('smallSubject')} ans={q.get('answer')}")
        print("  Q:",repr(q.get('question'))[:220])
        for L in 'ABCD':
            print(f"  {L}:",repr(q.get(L))[:160])
        print()
