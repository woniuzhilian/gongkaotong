# -*- coding: utf-8 -*-
import json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
q=json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))
print('sample yearQnum:', [(x['id'],x['year'],x['yearQnum']) for x in q[:5]])
seen=collections.Counter((x['year'],x['yearQnum']) for x in q)
dups=[k for k,v in seen.items() if v>1]
print('dup (year,yearQnum):', len(dups), dups[:10])
print('unique pairs:', len(seen))
# 公共基础 years
print(collections.Counter(x['year'] for x in q if x['bigSubject']=='公共基础'))
# check id ordering vs year
