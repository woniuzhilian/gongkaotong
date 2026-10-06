# -*- coding: utf-8 -*-
"""Render the full question block (stem .. next question) per question across pages."""
import sys, os, re, json, io, pymupdf
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
PRO=os.path.join(PDFDIR,"岩土专业基础历年真题试题册（2024版）.pdf")
OUT=r"C:\Users\Administrator\.qclaw\workspace\blocks"; os.makedirs(OUT,exist_ok=True)
ANY=re.compile(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】')
PRONUM=re.compile(r'(?m)^\s*(\d{1,3})\s*[、.]')
def norm(s):
    s=re.sub(r'<[^>]+>','',str(s)); s=re.sub(r'\{[^}]*\}','',s); s=s.replace('$','').replace('\\','')
    return ''.join(ch for ch in s if '\u4e00'<=ch<='\u9fff' or ch.isalnum())
DOCS={"公共基础":pymupdf.open(PUB),"专业基础":pymupdf.open(PRO)}
Q={q['id']:q for q in json.load(open(r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json",encoding='utf-8'))}
def charpos(txt,k):
    kk=0
    for i,ch in enumerate(txt):
        if '\u4e00'<=ch<='\u9fff' or ch.isalnum(): kk+=1
        if kk>=k: return i
    return 0
def words_below(page,y):
    return [w for w in page.get_text("words") if w[1]>=y-1]
def y_of_words(page, ws):
    return min((w[1] for w in ws), default=page.rect.y0)
def locate(doc,probe):
    for i in range(len(doc)):
        if probe in norm(doc[i].get_text()): return i
    return None
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002,94,451,560,561,682,695,1151,1155,1218,1391,1680,1932]
def next_marker_y(page,bs,yfrom):
    t=page.get_text()
    pat = ANY if bs=="公共基础" else PRONUM
    for m in pat.finditer(t):
        # find word position for this marker
        frag=t[m.start():m.start()+12]
        y=None
        for w in page.get_text("words"):
            if w[4].startswith(frag[:4]) and w[1]>=yfrom-1:
                y=w[1]; break
        if y is not None: return y
    return page.rect.y1
for qid in IDS:
    q=Q[qid]; bs=q['bigSubject']; doc=DOCS[bs]
    raw=re.sub(r'<[^>]+>','',q['question']); nq=norm(raw)
    pi=None
    for L in (26,20,14,10,8,6):
        if len(nq)>=L:
            pi=locate(doc,nq[:L])
            if pi is not None: break
    if pi is None: print(f"id{qid} NOTFOUND"); continue
    t=doc[pi].get_text(); pos=charpos(t,len(nq[:max(8,min(20,len(nq)))]))
    ytop=0
    for w in doc[pi].get_text("words"):
        if t.find(w[4])<=pos: ytop=max(ytop,w[1])
    # find end: next marker
    yend=next_marker_y(doc[pi],bs,ytop+3)
    pages=[pi]
    if yend>=doc[pi].rect.y1-1 and pi+1<len(doc):
        pages.append(pi+1)
    ims=[]
    for k,pg in enumerate(pages):
        page=doc[pg]
        if k==0: r=pymupdf.Rect(30, ytop-4, page.rect.x1-20, yend if yend>ytop else page.rect.y1)
        else:
            r=pymupdf.Rect(30, page.rect.y0, page.rect.x1-20, next_marker_y(page,bs,page.rect.y0))
        ims.append(Image.open(io.BytesIO(page.get_pixmap(clip=r,dpi=150).tobytes("png"))).convert("RGB"))
    W=max(i.width for i in ims); H=sum(i.height for i in ims)+6*(len(ims)-1)
    cv=Image.new("RGB",(W,H),"white"); yy=0
    for i in ims: cv.paste(i,(0,yy)); yy+=i.height+6
    fn=os.path.join(OUT,f"q{qid}.png"); cv.save(fn)
    print(f"id{qid} {bs} p{pi+1}..{pages[-1]+1} -> q{qid}.png {W}x{H}")
