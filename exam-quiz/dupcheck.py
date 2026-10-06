import json, io
p=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
d=json.load(io.open(p,encoding="utf-8"))
from collections import defaultdict
g=defaultdict(list)
for q in d:
    g[(q.get("bigSubject"),q.get("year"),q.get("yearQnum"))].append(q["id"])
targets=[(306,),]
broken=[306,448,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,2002]
byid={q["id"]:q for q in d}
out=[]
for i in broken:
    q=byid[i]
    key=(q.get("bigSubject"),q.get("year"),q.get("yearQnum"))
    out.append("broken id=%d key=%s -> dup_ids=%s"%(i,key,g[key]))
# count dup keys overall
ndup=sum(1 for k,v in g.items() if len(v)>1)
out.append("total duplicate (subj,year,num) keys: %d"%ndup)
io.open(r"C:\Users\Administrator\.qclaw\workspace\dups.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
