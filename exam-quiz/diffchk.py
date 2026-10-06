# -*- coding: utf-8 -*-
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\exam-quiz\src\data"
A={q['id']:q for q in json.load(open(os.path.join(D,"questions_BACKUP_20260913_104530.json"),encoding='utf-8'))}
B={q['id']:q for q in json.load(open(os.path.join(D,"questions.json"),encoding='utf-8'))}
assert set(A)==set(B), "id set changed!"
changed=[]
for i in sorted(A):
    for k in A[i]:
        if A[i][k]!=B[i][k]:
            changed.append((i,k))
ids=sorted(set(i for i,k in changed))
print("changed questions:",ids)
print("count:",len(ids),"fields:",len(changed))
exp={94,447,451,538,560,561,658,682,695,840,1626}
print("unexpected:",set(ids)-exp)
