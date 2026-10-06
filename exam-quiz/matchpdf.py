# -*- coding: utf-8 -*-
"""Match each broken JSON question's text to its true PDF block (marker-based)."""
import pymupdf, io, re, json, difflib
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
PRO=BASE+r"\岩土专业基础分类真题解析（16~24）_题目.pdf"
QJ=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"

def norm(s):
    s=re.sub(r"<[^>]+>","",s or "")
    s=s.replace("\\","").replace("$","").replace("~","")
    s=re.sub(r"[\s\u3000]+","",s)
    return s

def blocks(path):
    doc=pymupdf.open(path)
    pages=[doc[p].get_text() for p in range(doc.page_count)]
    doc.close()
    txt="".join("\n<<<P%d>>>\n"%i+t for i,t in enumerate(pages))
    mark=re.compile(r"【\s*(\d{4})\s*(补)?\s*-\s*(\d{1,3})\s*】")
    ms=list(mark.finditer(txt))
    bl=[]
    for i,m in enumerate(ms):
        key="%s%s-%s"%(m.group(1),"补" if m.group(2) else "",m.group(3))
        end=ms[i+1].start() if i+1<len(ms) else len(txt)
        seg=txt[m.start():end]
        pg=int(re.search(r"<<<P(\d+)>>>",txt[:m.start()][-40:]).group(1)) if re.search(r"<<<P(\d+)>>>",txt[:m.start()][-40:]) else -1
        bl.append((key,pg,seg))
    return bl

pub=blocks(PUB); pro=blocks(PRO)
print("pub blocks",len(pub),"pro blocks",len(pro))

d=json.load(io.open(QJ,encoding="utf-8"))
byid={q["id"]:q for q in d}
broken=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,2002]

def best(qtext, bl):
    nq=norm(qtext)
    scores=[]
    for key,pg,seg in bl:
        ns=norm(seg)
        r=difflib.SequenceMatcher(None,nq[:60],ns[:400]).ratio()
        scores.append((r,key,pg))
    scores.sort(reverse=True)
    return scores[:3]

out=[]
for i in broken:
    q=byid[i]
    bl=pub if q["bigSubject"]=="公共基础" else pro
    top=best(q.get("question",""),bl)
    out.append("id=%d %s %s-%s ans=%s"%(i,q["bigSubject"],q["year"],q["yearQnum"],q["answer"]))
    out.append("  Q:"+norm(q.get("question",""))[:80])
    for r,key,pg in top:
        out.append("   %.2f  %s (p%s)"%(r,key,pg))
    out.append("")
io.open(r"C:\Users\Administrator\.qclaw\workspace\matchpdf.txt","w",encoding="utf-8").write("\n".join(out))
print("done")
