# -*- coding: utf-8 -*-
import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
Q=json.load(open(r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json",encoding='utf-8'))
Qd={q['id']:q for q in Q}
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002,1987,1988,1888,840,694,815,1175,94,451,560,561,682,695,1151,1155,1218,1391,1680,1932]
out=[]
for qid in IDS:
    q=Qd[qid]
    out.append(json.dumps(q, ensure_ascii=False, indent=1))
open(r"C:\Users\Administrator\.qclaw\workspace\dump_full.json","w",encoding="utf-8").write("\n".join(out))
print("written", len(out))
