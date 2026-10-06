# -*- coding: utf-8 -*-
import re, os, json, difflib, sys
sys.stdout.reconfigure(encoding="utf-8")
O=r"C:\Users\Administrator\.qclaw\workspace\pdftxt"
def blocks(fn):
    txt=open(os.path.join(O,fn),encoding="utf-8").read()
    txt=re.sub(r"\n===== PAGE \d+ =====\n","\n",txt)
    parts=re.split(r"(【\d{4}(?:补)?-\d+】)",txt)
    res={}
    for i in range(1,len(parts),2):
        res[parts[i]]=parts[i+1].strip()
    return res
bq=blocks("pubQ.txt"); ba=blocks("pubA.txt")

def norm(s):
    s=re.sub(r"<br\s*/?>","",s)
    s=re.sub(r"<img[^>]*>","",s)
    s=re.sub(r"\$[^$]*\$","",s)
    s=re.sub(r"\\[a-zA-Z]+","",s)
    s=re.sub(r"[\s\u3000,，.。;；:：()（）\[\]【】\-—_/、'\"“”‘’]+","",s)
    return s

P=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
data=json.load(open(P,encoding='utf-8'))
qids=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002]
def sim(a,b):
    if not a or not b: return 0
    return difflib.SequenceMatcher(None,a,b).ratio()
out=open(os.path.join(O,"match.txt"),"w",encoding="utf-8")
for q in data:
    if q['id'] not in qids: continue
    nq=norm(q.get('question',''))
    best=None
    for tag,body in bq.items():
        nb=norm(body)
        # quick: containment of first 16 chars
        r=sim(nq,nb[:len(nq)+40])
        if best is None or r>best[0]:
            best=(r,tag)
    out.write(f"id={q['id']} jsonY={q['year']}-{q['yearQnum']}  BEST {best[1]}  r={best[0]:.3f}\n")
out.close()
print("done")
