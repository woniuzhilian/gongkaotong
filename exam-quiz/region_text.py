# -*- coding: utf-8 -*-
import sys, os, re, json, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
PRO=os.path.join(PDFDIR,"岩土专业基础历年真题试题册（2024版）.pdf")
Q=json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))
Qd={q['id']:q for q in Q}
ANYMK=re.compile(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】')
def mr(y,n): return re.compile(r'【\s*'+re.escape(str(y))+r'\s*补?\s*[-–]\s*'+re.escape(str(n))+r'\s*】')
def region(doc,y,n):
    rx=mr(y,n)
    for i in range(len(doc)):
        t=doc[i].get_text()
        m=rx.search(t)
        if m:
            nxt=ANYMK.search(t, m.end())
            end=nxt.start() if nxt else len(t)
            return doc[i].get_text()[m.start():end], i+1
    return None,None
dubs={"PUB":pymupdf.open(PUB),"PRO":pymupdf.open(PRO)}
TARGETS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002,1987,1988]
for qid in TARGETS:
    q=Qd[qid]
    for tag,doc in dubs.items():
        r,pg=region(doc,q['year'],q['yearQnum'])
        if r:
            print(f"########## id{qid} [{tag} p{pg}] {q['year']}-{q['yearQnum']} ##########")
            print(re.sub(r'\n\s*\n','\n', r.strip())[:900])
            print()
            break
    else:
        print(f"########## id{qid} NOTFOUND ##########\n")
