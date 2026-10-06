# -*- coding: utf-8 -*-
import sys, os, re, json, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
PRO=os.path.join(PDFDIR,"岩土专业基础历年真题试题册（2024版）.pdf")
PUBANS=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_答案解析.pdf")
PROANS=os.path.join(PDFDIR,"岩土专业基础历年真题解析册（2024版）.pdf")
ANYMK=re.compile(r'【\s*(\d{4})\s*(补?)\s*[-–]\s*(\d+)\s*】')
def norm(s):
    s=re.sub(r'<[^>]+>','',str(s)); s=re.sub(r'\{[^}]*\}','',s); s=re.sub(r'\$[^$]*\$','',s)
    s=re.sub(r'\\([A-Za-z]+)',r'\1',s)
    return ''.join(ch for ch in s if '\u4e00'<=ch<='\u9fff' or ch.isalnum())

docs={"公共基础":pymupdf.open(PUB),"专业基础":pymupdf.open(PRO)}
def find_in(doc, probe):
    """return (pageidx, label)"""
    for i in range(len(doc)):
        t=doc[i].get_text(); nt=norm(t)
        j=nt.find(probe)
        if j<0: continue
        # find nearest label whose normalized offset <= j
        best=None
        for m in ANYMK.finditer(t):
            # normalized offset of this marker
            off=len(norm(t[:m.start()]))
            if off<=j+2:
                best=(off, m.group(0))
        return i, (best[1] if best else "?"), j
    return None,None,None

Q={q['id']:q for q in json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))}
PIDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002,1987,1988,1888,840,694,815,1175,1151,1155,1218,1391,1680,1932,682,94,451,560,561,695,930]
out=[]
for qid in PIDS:
    q=Q[qid]; doc=docs[q['bigSubject']]
    raw=re.sub(r'<[^>]+>','',q['question']); nr=norm(raw)
    found=None
    for L in (24,16,12,8):
        if len(nr)>=L and L>=8:
            p=nr[:L]
            pi,lab,j=find_in(doc,p)
            if pi is not None:
                found=(pi,lab,p); break
    if found:
        pi,lab,p=found
        out.append(f"id{qid} json={q['year']}-{q['yearQnum']} [{q['smallSubject']}] -> PDF p{pi+1} label={lab} probe={p!r}")
    else:
        out.append(f"id{qid} json={q['year']}-{q['yearQnum']} [{q['smallSubject']}] -> NO MATCH (stem={raw[:40]!r})")
print("\n".join(out))
open(r"C:\Users\Administrator\.qclaw\workspace\mapcheck.txt","w",encoding="utf-8").write("\n".join(out))
