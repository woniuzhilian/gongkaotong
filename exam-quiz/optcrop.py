# -*- coding: utf-8 -*-
"""Cluster figure objects in a question region and assign each to the nearest option label below it."""
import sys, os, re, json, io, pymupdf
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
PRO=os.path.join(PDFDIR,"岩土专业基础历年真题试题册（2024版）.pdf")
OUT=r"C:\Users\Administrator\.qclaw\workspace\optcrop"; os.makedirs(OUT,exist_ok=True)
ANY=re.compile(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】')
PRONUM=re.compile(r'(?m)^\s*(\d{1,3})\s*[、.]')
LBL=re.compile(r'[（(]([A-D])[）)]')
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
def locate(doc,probe):
    for i in range(len(doc)):
        if probe in norm(doc[i].get_text()): return i
    return None
def clusters(objs, gap=12):
    objs=sorted(objs,key=lambda b:(b[1],b[0])); merged=[]
    for b in objs:
        for m in merged:
            if not (b[2]<m[0]-gap or b[0]>m[2]+gap or b[3]<m[1]-gap or b[1]>m[3]+gap):
                m[0]=min(m[0],b[0]); m[1]=min(m[1],b[1]); m[2]=max(m[2],b[2]); m[3]=max(m[3],b[3]); break
        else: merged.append(list(b))
    # second pass
    changed=True
    while changed:
        changed=False; out=[]
        for b in merged:
            for m in out:
                if not (b[2]<m[0]-gap or b[0]>m[2]+gap or b[3]<m[1]-gap or b[1]>m[3]+gap):
                    m[0]=min(m[0],b[0]); m[1]=min(m[1],b[1]); m[2]=max(m[2],b[2]); m[3]=max(m[3],b[3]); changed=True; break
            else: out.append(b)
        merged=out
    return merged
def process(qid):
    q=Q[qid]; bs=q['bigSubject']; doc=DOCS[bs]
    raw=re.sub(r'<[^>]+>','',q['question']); nq=norm(raw)
    pi=None
    for L in (26,20,14,10,8,6):
        if len(nq)>=L:
            pi=locate(doc,nq[:L])
            if pi is not None: break
    if pi is None: return None
    pages=[pi]
    t=doc[pi].get_text(); pos=charpos(t,len(nq[:max(8,min(20,len(nq)))]))
    ytop=max((w[1] for w in doc[pi].get_text("words") if t.find(w[4])<=pos), default=0)
    # collect option labels across pages
    labels=[]  # (L, x, y, page)
    for pg in (pi, pi+1 if pi+1<len(doc) else pi):
        page=doc[pg]
        for w in page.get_text("words"):
            m=LBL.search(w[4])
            if not m: continue
            if pg==pi and w[1]<ytop+2: continue
            labels.append((m.group(1), w[0], w[1], w[3], pg))
    labels.sort(key=lambda z:(round(z[2]/40), z[1]))
    # collect figure objects
    figs=[]
    for pg in (pi, pi+1 if pi+1<len(doc) else pi):
        page=doc[pg]
        for im in page.get_image_info():
            b=im['bbox']
            if pg==pi and b[3]<ytop-4: continue
            figs.append((pg,)+tuple(b))
        for d in page.get_drawings():
            b=d['rect']
            if b.width<4 or b.height<4: continue
            if pg==pi and b.y1<ytop-4: continue
            figs.append((pg, b.x0,b.y0,b.x1,b.y1))
    # cluster per page
    cl=[]
    for pg in set(f[0] for f in figs):
        cl+= [ (pg,)+tuple(b) for b in clusters([f[1:] for f in figs if f[0]==pg]) ]
    # ytop bound for first page
    cl=[c for c in cl if not (c[0]==pi and c[2]<ytop-4)]
    # assign each cluster to nearest label below (same page, label.y>=cluster.y)
    assigns={}
    for pg,x0,y0,x1,y1 in cl:
        cand=[l for l in labels if l[4]==pg and l[2]>=y0-2]
        if not cand: continue
        # nearest by vertical then horizontal overlap
        cand.sort(key=lambda l:(l[2]-y1, abs(((l[1]) - (x0+x1)/2))))
        L=cand[0][0]
        assigns.setdefault(L,[]).append((pg,x0,y0,x1,y1))
    tiles=[]
    for L in "ABCD":
        boxes=assigns.get(L,[])
        if not boxes: continue
        if len(boxes)==1:
            pg,x0,y0,x1,y1=boxes[0]
            r=pymupdf.Rect(x0-4,y0-4,x1+4,y1+4)
            im=Image.open(io.BytesIO(doc[pg].get_pixmap(clip=r,dpi=200).tobytes("png"))).convert("RGB")
            d=ImageDraw.Draw(im); d.rectangle([0,0,im.width-1,im.height-1],outline="red",width=3); d.text((5,5),L,fill="red")
            tiles.append(im)
        else:
            ims=[]
            for pg,x0,y0,x1,y1 in boxes:
                r=pymupdf.Rect(x0-3,y0-3,x1+3,y1+3)
                ims.append(Image.open(io.BytesIO(doc[pg].get_pixmap(clip=r,dpi=200).tobytes("png"))).convert("RGB"))
            w=max(i.width for i in ims); h=sum(i.height for i in ims)+4*(len(ims)-1)
            im=Image.new("RGB",(w,h),"white"); yy=0
            for t2 in ims: im.paste(t2,(0,yy)); yy+=t2.height+4
            d=ImageDraw.Draw(im); d.rectangle([0,0,im.width-1,im.height-1],outline="red",width=3); d.text((5,5),L,fill="red")
            tiles.append(im)
    if not tiles: return None
    W=sum(t2.width for t2 in tiles)+10*(len(tiles)+1); H=max(t2.height for t2 in tiles)+20
    cv=Image.new("RGB",(W,H),"white"); xx=10
    for t2 in tiles: cv.paste(t2,(xx,10)); xx+=t2.width+10
    fn=os.path.join(OUT,f"q{qid}.png"); cv.save(fn)
    return fn, {L:len(assigns.get(L,[])) for L in "ABCD"}
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002]
for qid in IDS:
    r=process(qid)
    print(qid, r[1] if r else "NONE", os.path.basename(r[0]) if r else "")
