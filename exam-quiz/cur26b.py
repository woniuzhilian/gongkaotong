import json, io, sys
p=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
d=json.load(io.open(p,encoding="utf-8"))
out=[]
for q in d:
    k=q.get("id")
    A=(q.get("A") or "").strip(); B=(q.get("B") or "").strip(); C=(q.get("C") or "").strip(); D=(q.get("D") or "").strip()
    if not B or not C or not D:
        out.append((k,q.get("bigSubject"),q.get("year"),q.get("yearQnum"),q.get("answer"),
                    (q.get("question") or "")[:60],
                    A[:60],B[:60],C[:60],D[:60]))
print("broken count:",len(out))
for r in out:
    print(r[0],"|",r[1],"|",r[2],"|",r[3],"| ans",r[4])
    print("   Q:",r[5])
    print("   A:",r[6])
    print("   B:",r[7])
    print("   C:",r[8])
    print("   D:",r[9])
