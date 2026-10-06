# -*- coding: utf-8 -*-
"""For the 26 empty-option questions, extract region text + per-option text/figure."""
import sys, os, re, json, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
PRO=os.path.join(PDFDIR,"岩土专业基础历年真题试题册（2024版）.pdf")
ANY=re.compile(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】')
PRONUM=re.compile(r'(?m)^\s*(\d{1,3})\s*[、.]')
def norm(s):
    s=re.sub(r'<[^>]+>','',str(s)); s=re.sub(r'\{[^}]*\}','',s); s=s.replace('$','').replace('\\','')
    return ''.join(ch for ch in s if '\u4e00'<=ch<='\u9fff' or ch.isalnum())
DOCS={"公共基础":pymupdf.open(PUB),"专业基础":pymupdf.open(PRO)}
Q={q['id']:q for q in json.load(open(r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json",encoding='utf-8'))}
def locate(doc,probe):
    for i in range(len(doc)):
        if probe in norm(doc[i].get_text()): return i
    return None
def region(doc,pi,bs,probe):
    t=doc[pi].get_text(); nt=norm(t); j=nt.find(probe); k=0; idx=0
    for idx,ch in enumerate(t):
        if '\u4e00'<=ch<='\u9fff' or ch.isalnum(): k+=1
        if k>=j+1: break
    start=idx
    if bs=="公共基础":
        m=ANY.search(t,start); end=m.start() if m else len(t)
    else:
        end=len(t)
        for mm in PRONUM.finditer(t):
            if mm.start()>start: end=mm.start(); break
    return t[start:end], pi+1
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002]
out=[]
for qid in IDS:
    q=Q[qid]; doc=DOCS[q['bigSubject']]; raw=re.sub(r'<[^>]+>','',q['question']); nq=norm(raw)
    pi=None
    for L in (26,20,14,10):
        if len(nq)>=L:
            pi=locate(doc,nq[:L])
            if pi is not None: break
    if pi is None:
        out.append(f"\n### id{qid} NOTFOUND stem={raw[:50]!r}"); continue
    txt,pg=region(doc,pi,q['bigSubject'],nq[:max(8,min(20,len(nq)))])
    flat=re.sub(r'[ \t]+',' ',txt)
    out.append(f"\n### id{qid} {q['bigSubject']} {q['year']}-{q['yearQnum']} p{pg} ans={q['answer']}")
    out.append(flat.strip()[:800])
print("\n".join(out))
open(r"C:\Users\Administrator\.qclaw\workspace\region26.txt","w",encoding="utf-8").write("\n".join(out))
