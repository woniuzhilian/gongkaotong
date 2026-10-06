# -*- coding: utf-8 -*-
import sys, os, json, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
qs=json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))
Q={q['id']:q for q in qs}
pdfs=sorted([f for f in os.listdir(PDFDIR) if f.lower().endswith('.pdf')])
docs={}
for f in pdfs:
    try:
        docs[f]=pymupdf.open(os.path.join(PDFDIR,f))
    except Exception as e:
        print("open fail",f,e)

TARGETS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002,
         1987,1988,1888,840,694,815,1175,94,451,560,561,682,695,1151,1155,1218,1391,1680,1932]

def norm(s):
    # keep only CJK + alnum, strip img/math markup
    s=re.sub(r'<[^>]+>','',str(s))
    s=re.sub(r'\$[^$]*\$','',s)
    s=re.sub(r'[^\u4e00-\u9fff0-9A-Za-z]','',s)
    return s

for qid in TARGETS:
    q=Q[qid]
    stem=norm(q['question'])
    probe=stem[:20]
    found=[]
    for f,doc in docs.items():
        for i in range(len(doc)):
            t=doc[i].get_text()
            if probe and probe in norm(t):
                found.append((f,i+1)); break
    print(f"id{qid} {q['year']}-{q['yearQnum']} :: {probe[:26]} -> {found}")
