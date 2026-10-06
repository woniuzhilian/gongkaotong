# -*- coding: utf-8 -*-
import sys, json, re, os, html
sys.stdout.reconfigure(encoding='utf-8')
P=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
data=json.load(open(P,encoding='utf-8'))
qids=[306,448,546,568,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002,658]
def imgs(s):
    return re.findall(r'/images/([^"\']+)', s or '')
for q in data:
    if q['id'] not in qids: continue
    print(f"id={q['id']} {q['year']}-{q['yearQnum']} ans={q['answer']}")
    print("   STEM imgs:", imgs(q.get('question','')))
    for L in 'ABCD':
        ii=imgs(q.get(L,''))
        if ii: print(f"   {L} imgs:", ii)
    print()
