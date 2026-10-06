# -*- coding: utf-8 -*-
import sys, os, re, json, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
PRO=os.path.join(PDFDIR,"岩土专业基础历年真题试题册（2024版）.pdf")
ANYMK=re.compile(r'【\s*(\d{4})\s*(补?)\s*[-–]\s*(\d+)\s*】')
def norm(s):
    s=re.sub(r'<[^>]+>','',str(s)); s=re.sub(r'\{[^}]*\}','',s); s=re.sub(r'\$[^$]*\$','',s)
    s=re.sub(r'\\([A-Za-z]+)',r'\1',s)
    return ''.join(ch for ch in s if '\u4e00'<=ch<='\u9fff' or ch.isalnum())
docs={"公共基础":pymupdf.open(PUB),"专业基础":pymupdf.open(PRO)}

def locate(doc, probe):
    hits=[]
    for i in range(len(doc)):
        t=norm(doc[i].get_text())
        j=t.find(probe)
        if j>=0: hits.append(i)
    return hits

targets=[447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1262,1292,94,451,560,561,682,695,1218,1391]
Q={q['id']:q for q in json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))}
for qid in targets:
    q=Q[qid]; doc=docs[q['bigSubject']]
    raw=re.sub(r'<[^>]+>','',q['question'])
    for L in (20,14,10,8):
        p=norm(raw)[:L]
        if len(p)<6: continue
        h=locate(doc,p)
        if h: break
    # label near first hit
    lab=""
    if h:
        pg=doc[h[0]].get_text()
        mlist=list(ANYMK.finditer(pg))
        # pick last label before the matched position
        print(f"id{qid} json={q['year']}-{q['yearQnum']} probe={p!r} pages={[x+1 for x in h]} labels_on_p1={[m.group(0) for m in mlist]}")
    else:
        print(f"id{qid} json={q['year']}-{q['yearQnum']} probe={p!r} NOLOC")
