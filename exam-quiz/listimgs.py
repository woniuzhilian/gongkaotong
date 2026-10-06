# -*- coding: utf-8 -*-
import sys, os, re, json, glob
sys.stdout.reconfigure(encoding='utf-8')
IMG=r"E:\应用程序开发\刷题\exam-quiz\public\images"
files=os.listdir(IMG)
Q={q['id']:q for q in json.load(open(r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json",encoding='utf-8'))}
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002]
def imgs(s): return re.findall(r'<img[^>]*src="([^"]+)"', s or '')
for qid in IDS:
    q=Q[qid]
    refs=[]
    for fld in ["question","A","B","C","D"]: refs+=imgs(q[fld])
    # count total referenced distinct
    pref=set()
    for u in refs:
        b=os.path.basename(u)
        m=re.match(r'(id\d+_\d+_\d+)', b)
        if m: pref.add(m.group(1))
        m2=re.match(r'(id\d+_\d{4}补?_\d+)', b)
        if m2: pref.add(m2.group(1))
    allf=set()
    for p in pref:
        allf |= {f for f in files if f.startswith(p)}
    print(f"id{qid} {q['year']}-{q['yearQnum']}: refs={len(refs)} prefixes={sorted(pref)}")
    print(f"    candidate files: {sorted(allf)}")
