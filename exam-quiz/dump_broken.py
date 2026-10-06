# -*- coding: utf-8 -*-
import json, io
p=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
d=json.load(io.open(p,encoding="utf-8"))
ids=[306,448,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,2002]
byid={q["id"]:q for q in d}
lines=[]
for i in ids:
    q=byid[i]
    lines.append("="*70)
    lines.append("id=%s big=%s year=%s yq=%s ans=%s"%(i,q.get("bigSubject"),q.get("year"),q.get("yearQnum"),q.get("answer")))
    lines.append("Q: "+str(q.get("question")))
    lines.append("A: "+str(q.get("A")))
    lines.append("B: "+str(q.get("B")))
    lines.append("C: "+str(q.get("C")))
    lines.append("D: "+str(q.get("D")))
    lines.append("ANA: "+str(q.get("analysis"))[:300])
io.open(r"C:\Users\Administrator\.qclaw\workspace\broken23.txt","w",encoding="utf-8").write("\n".join(lines))
print("done")
