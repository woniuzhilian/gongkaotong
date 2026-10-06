# -*- coding: utf-8 -*-
"""Extract option figures for target questions from the classified PUB PDF, using label positions and bounded marker regions."""
import sys, os, re, json, io, pymupdf
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
STAGE=r"C:\Users\Administrator\.qclaw\workspace\optstage"
os.makedirs(STAGE, exist_ok=True)
MK=re.compile(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】')

def marker_re(y,n):
    return re.compile(r'【\s*'+str(y)+r'\s*补?\s*[-–]\s*'+str(n)+r'\s*】')

def marker_y(page, rex):
    for w in page.get_text("words"):
        if rex.search(w[4]):
            return w[1]
    return None

def region_pages(doc, y, n, span=2):
    rex=marker_re(y,n)
    for i in range(len(doc)):
        yy=marker_y(doc[i], rex)
        if yy is not None:
            return i, yy
    return None, None

def extract(doc, y, n, qid):
    pi, y0 = region_pages(doc, y, n)
    if pi is None: return None
    # collect (page, top_y, bottom_y) region pieces until next marker
    nextrex=None
    pieces=[]
    top=y0
    for step in range(0,3):
        idx=pi+step
        if idx>=len(doc): break
        page=doc[idx]
        # candidate next marker y (any marker) strictly after top
        nxt=None
        for w in page.get_text("words"):
            if MK.search(w[4]) and w[1] > top+5:
                nxt=w[1]; break
        bottom = nxt if nxt is not None else page.rect.y1-16
        pieces.append((idx, top, bottom))
        if nxt is not None: break
        top=50
    # gather labels and images across pieces
    labels={}  # letter -> (page,bbox)
    imgs=[]    # (page,bbox)
    for idx, a, b in pieces:
        page=doc[idx]
        for w in page.get_text("words"):
            mm=re.search(r'（([A-D])）', w[4])
            if mm and a-3 <= w[1] <= b+3:
                labels.setdefault(mm.group(1), (idx,(w[0],w[1],w[2],w[3])))
        for im in page.get_image_info():
            x0,iy0,x1,iy1=im['bbox']
            if iy0>=a-8 and iy0<=b+40:
                imgs.append((idx,(x0,iy0,x1,iy1)))
    res={}
    for L in "ABCD":
        if L not in labels: continue
        idx,lb=labels[L]
        lx0,ly0,lx1,ly1=lb
        # image slightly below label, x-overlap, y within 150
        best=None
        for pi2,b in imgs:
            if pi2!=idx: 
                # allow same-page only for pairing simplicity
                continue
            ix0,iy0,ix1,iy1=b
            ov=min(lx1,ix1)-max(lx0,ix0)
            gap=iy0-ly1
            if ov>0 and -5<=gap<=150:
                sc=(ov,-abs(gap))
                if best is None or sc>best[0]: best=(sc,b)
        if best:
            b=best[1]
            ux0=min(lx0,b[0]); uy0=min(ly0,b[1]); ux1=max(lx1,b[2]); uy1=max(ly1,b[3])
            res[L]=(idx,(ux0,uy0,ux1,uy1))
    # crop
    out={}
    for L,(idx,b) in res.items():
        page=doc[idx]
        clip=pymupdf.Rect(max(0,b[0]-5),max(0,b[1]-5),min(page.rect.x1,b[2]+5),min(page.rect.y1,b[3]+5))
        pix=page.get_pixmap(clip=clip, dpi=200)
        out[L]=(idx,pix)
    return out

def contact(qid, out):
    if not out: return None
    tiles=[]
    for L in "ABCD":
        if L not in out: continue
        idx,pix=out[L]
        im=Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        d=ImageDraw.Draw(im); d.rectangle([0,0,im.width-1,im.height-1],outline="red",width=2)
        d.text((4,4), L, fill="red")
        tiles.append(im)
    W=sum(t.width for t in tiles)+10*(len(tiles)+1); H=max(t.height for t in tiles)+20
    cv=Image.new("RGB",(W,H),"white"); xx=10
    for t in tiles: cv.paste(t,(xx,10)); xx+=t.width+10
    fn=os.path.join(STAGE,f"q{qid}_sheet.png"); cv.save(fn); return fn

Q=json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))
Qd={q['id']:q for q in Q}
TARGETS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1262,1292]
dub=pymupdf.open(PUB)
for qid in TARGETS:
    q=Qd[qid]
    out=extract(dub, q['year'], q['yearQnum'], qid)
    got=sorted(out.keys()) if out else []
    fn=contact(qid,out) if out else None
    print(f"id{qid} {q['year']}-{q['yearQnum']} -> opts {got} {os.path.basename(fn) if fn else ''}")
