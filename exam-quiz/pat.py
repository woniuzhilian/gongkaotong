# -*- coding: utf-8 -*-
import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
P=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
data=json.load(open(P,encoding='utf-8'))
print("total",len(data))
cnt=0
for q in data:
    opts={k:q.get(k,'') for k in 'ABCD'}
    withimg=[k for k,v in opts.items() if 'images/' in (v or '')]
    if withimg:
        cnt+=1
        if cnt<=25:
            print("id",q['id'],q['year'],q['yearQnum'],"->",{k:(opts[k][:70]) for k in 'ABCD'})
print("total questions with img in ANY option:",cnt)
# count patterns: how many options contain image
from collections import Counter
c=Counter()
for q in data:
    n=sum(1 for k in 'ABCD' if 'images/' in (q.get(k) or ''))
    c[n]+=1
print("distribution of #options-with-image:",dict(c))
