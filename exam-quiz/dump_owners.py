import json, io
p=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
d=json.load(io.open(p,encoding="utf-8"))
byid={q["id"]:q for q in d}
ids=[1047,1052,1073,1142,1144,1148,762,718,1099,1102,1110,1140,1141,787,788,813,993,832,834,822,821,658,666]
out=[]
for i in ids:
    q=byid.get(i)
    if not q: out.append("id=%s MISSING"%i); continue
    out.append("id=%s big=%s year=%s yq=%s ans=%s"%(i,q.get("bigSubject"),q.get("year"),q.get("yearQnum"),q.get("answer")))
    out.append("  Q: "+str(q.get("question"))[:200])
    for k in "ABCD": out.append("  %s: %s"%(k,str(q.get(k))[:160]))
    out.append("")
io.open(r"C:\Users\Administrator\.qclaw\workspace\owner_ids.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
