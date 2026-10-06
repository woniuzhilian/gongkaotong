# -*- coding: utf-8 -*-
import sys, os, re, json, shutil
sys.stdout.reconfigure(encoding='utf-8')
ROOT=r"E:\应用程序开发\刷题\exam-quiz"
PUBIMG=os.path.join(ROOT,"public")
DST=r"C:\Users\Administrator\.qclaw\workspace\imgs"
os.makedirs(DST, exist_ok=True)
Q={q['id']:q for q in json.load(open(os.path.join(ROOT,'src','data','questions.json'),encoding='utf-8'))}
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002]
def imgs(s): return re.findall(r'<img[^>]*src="([^"]+)"', s or '')
rep=[]
for qid in IDS:
    q=Q[qid]
    for fld in ["question","A","B","C","D"]:
        for u in imgs(q[fld]):
            src=os.path.join(PUBIMG, u.lstrip('/').replace('/',os.sep))
            if os.path.exists(src):
                base=f"q{qid}_{fld}_{os.path.basename(u)}"
                shutil.copy(src, os.path.join(DST,base))
                rep.append(f"{base}  {os.path.getsize(src)}B  <- {u}")
            else:
                rep.append(f"MISSING {u} (id{qid} {fld})")
print("\n".join(rep))
