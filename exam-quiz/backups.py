# -*- coding: utf-8 -*-
import sys, os, json, glob
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\exam-quiz"
cands=glob.glob(os.path.join(D,'**','questions*.json'),recursive=True)
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\backups.txt","w",encoding="utf-8")
for c in cands:
    OUT.write(f"{os.path.getsize(c):>10} {c}\n")
OUT.write("\n")
def load(p):
    try: return {q['id']:q for q in json.load(open(p,encoding='utf-8'))}
    except Exception as e: return None
ORIG=None
for c in cands:
    if 'ORIGINAL' in c: ORIG=load(c)
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002,94,451,560,561,682,695,1888,840]
for c in cands:
    if 'ORIGINAL' not in c: continue
    Q=load(c); OUT.write(f"\n##### {c}\n")
    for i in IDS:
        q=Q.get(i)
        if not q: OUT.write(f"id{i} missing\n"); continue
        empty=[L for L in "ABCD" if not q.get(L)]
        OUT.write(f"id{i} empty={''.join(empty) if empty else '-'} Q={q['question'][:40]!r}\n")
OUT.close(); print(open(r"C:\Users\Administrator\.qclaw\workspace\backups.txt",encoding='utf-8').read()[:4000])
