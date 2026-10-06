# -*- coding: utf-8 -*-
"""For each target question, locate its region in the source PDFs by stem text,
then dump the option text + figure presence, to drive data repair."""
import sys, os, re, json, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
PUBANS=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_答案解析.pdf")
PRO=os.path.join(PDFDIR,"岩土专业基础历年真题试题册（2024版）.pdf")
PROANS=os.path.join(PDFDIR,"岩土专业基础历年真题解析册（2024版）.pdf")
ANY=re.compile(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】')
PRONUM=re.compile(r'(?m)^\s*(\d{1,3})\s*[、.]')
def norm(s):
    s=re.sub(r'<[^>]+>','',str(s)); s=re.sub(r'\{[^}]*\}','',s)
    s=s.replace('$','').replace('\\','')
    return ''.join(ch for ch in s if '\u4e00'<=ch<='\u9fff' or ch.isalnum())
DOCS={"pub":pymupdf.open(PUB),"pubans":pymupdf.open(PUBANS),"pro":pymupdf.open(PRO),"proans":pymupdf.open(PROANS)}
def locate(doc,probe):
    for i in range(len(doc)):
        if probe in norm(doc[i].get_text()): return i
    return None
def region(doc,pi,kind,probe):
    t=doc[pi].get_text()
    nt=norm(t); j=nt.find(probe)
    # estimate char position in raw text
    k=0
    for idx,ch in enumerate(t):
        if '\u4e00'<=ch<='\u9fff' or ch.isalnum(): k+=1
        if k>=j+1: break
    else: idx=0
    start=idx
    if kind=="pub":
        m=ANY.search(t,start); end=m.start() if m else len(t)
    else:
        m=None
        for mm in PRONUM.finditer(t):
            if mm.start()>start: m=mm; break
        end=m.start() if m else len(t)
    return t[start:end], pi+1

Q={q['id']:q for q in json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))}
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002,1987,1988,1888,840,694,815,1175,94,451,560,561,682,695,1151,1155,1218,1391,1680,1932]
out=[]
for qid in IDS:
    q=Q[qid]; raw=re.sub(r'<[^>]+>','',q['question']); nq=norm(raw)
    out.append(f"\n################ id{qid} {q['bigSubject']} {q['year']}-{q['yearQnum']} [{q['smallSubject']}]")
    out.append("JSON: "+re.sub(r'<[^>]+>','&lt;IMG&gt;',q['question'])[:220])
    hit=False
    for tag,kind in (("pub","pub"),("pro","pro")):
        doc=DOCS[tag]
        pi=None
        for L in (26,20,14,10):
            if len(nq)>=L:
                pi=locate(doc,nq[:L])
                if pi is not None: break
        if pi is None: continue
        txt,pg=region(doc,pi,kind,nq[:max(8,min(20,len(nq)))])
        out.append(f"  >> {tag} p{pg}: "+re.sub(r'\s+',' ',txt)[:700])
        hit=True
    if not hit: out.append("  >> NOT FOUND in pub/pro")
print("\n".join(out))
open(r"C:\Users\Administrator\.qclaw\workspace\regions_all.txt","w",encoding="utf-8").write("\n".join(out))
