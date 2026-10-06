# -*- coding: utf-8 -*-
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
P=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
Q=json.load(open(P,encoding='utf-8'))
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002,
     94,451,560,561,682,695,1151,1155,1218,1391,1680,1932,1888,840,694,815,1175,1987,1988]
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\cur_targets.txt","w",encoding="utf-8")
for i in IDS:
    q=next((x for x in Q if x['id']==i),None)
    if not q: OUT.write(f"id{i} MISSING\n"); continue
    OUT.write(f"\n===== id{i} [{q['bigSubject']}] year={q['year']} yq={q['yearQnum']} ans={q['answer']}\n")
    OUT.write(f"Q: {q['question']!r}\n")
    for L in "ABCD": OUT.write(f"  {L}: {q[L]!r}\n")
    OUT.write(f"  ANA: {q['analysis']!r}\n")
OUT.close(); print("done")
