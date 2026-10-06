# -*- coding: utf-8 -*-
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
P=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
Q=json.load(open(P,encoding='utf-8'))
byid={q['id']:q for q in Q}
IDS=[306,448,546,568,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,2002]
out=open(r"C:\Users\Administrator\.qclaw\workspace\cur_full.txt","w",encoding="utf-8")
for i in IDS:
    q=byid[i]
    out.write(json.dumps(q,ensure_ascii=False,indent=1)+"\n")
out.close(); print("done")
