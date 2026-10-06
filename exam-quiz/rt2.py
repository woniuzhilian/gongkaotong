# -*- coding: utf-8 -*-
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
P=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
raw=open(P,'rb').read()
Q=json.loads(raw.decode('utf-8'))
d2=json.dumps(Q,ensure_ascii=False,indent=2).encode('utf-8')
print("cur bytes",len(raw))
print("redump bytes",len(d2))
print("equal",raw==d2)
# check no trailing newline
print("ends",raw[-5:])
