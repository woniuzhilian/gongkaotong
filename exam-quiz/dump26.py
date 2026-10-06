# -*- coding: utf-8 -*-
import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
ROOT=r"E:\应用程序开发\刷题\exam-quiz"
Q=json.load(open(os.path.join(ROOT,'src','data','questions.json'),encoding='utf-8'))
Qd={q['id']:q for q in Q}
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002]
def imgs(s):
    return re.findall(r'<img[^>]*src="([^"]+)"', s or '')
for qid in IDS:
    q=Qd[qid]
    print(f"=== id{qid} {q['bigSubject']} {q['year']}-{q['yearQnum']} [{q['smallSubject']}]")
    print("  Q:", re.sub(r'<[^>]+>',' <IMG>',q['question'])[:180])
    for L in "ABCD":
        v=q[L] or ''
        print(f"  {L}: {re.sub(chr(60)+'[^'+chr(62)+']+'+chr(62),' <IMG>',v)[:120]!r} imgs={imgs(v)}")
    print("  ans:", q['answer'], "| A(analysis):", re.sub(r'<[^>]+>','',q['analysis'])[:100])
