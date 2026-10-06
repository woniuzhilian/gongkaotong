# -*- coding: utf-8 -*-
"""Extract option figures (label + figure) for figure-choice questions."""
import sys, os, re, json, io, pymupdf
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
PRO=os.path.join(PDFDIR,"岩土专业基础历年真题试题册（2024版）.pdf")
STAGE=r"C:\Users\Administrator\.qclaw\workspace\optstage"
os.makedirs(STAGE, exist_ok=True)
ANYMK=re.compile(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】')

def marker_re(y,n):
    return re.compile(r'【\s*'+re.escape(str(y))+r'\s*补?\s*[-–]\s*'+re.escape(str(n))+r'\s*】')

def find_marker(doc,y,n):
    rex=marker_re(y,n)
    for i in range(len(doc)):
        for w in doc[i].get_text("words"):
            if rex.search(w[4]):
                return i, w[1]
    return None,None

def collect(doc, pi, y0):
    """Return (labels, imgs) where labels={L:(page,bbox)}, imgs=[(page,bbox)] within question region."""
    labels={}; imgs=[]
    top=y0
    for step in range(0,3):
        idx=pi+step
        if idx>=len(doc): break
        page=doc[idx]
        nxt=None
        for w in page.get_text("words"):
            if ANYMK.search(w[4]) and w[1] > top+5:
                nxt=w[1]; break
        bottom = nxt if nxt is not None else page.rect.y1-16
        for w in page.get_text("words"):
            mm=re.search(r'（([A-D])）', w[4])
            if mm and top-4 <= w[1] <= bottom+4:
                L=mm.group(1)
                if L not in labels: labels[L]=(idx,(w[0],w[1],w[2],w[3]))
        for im in page.get_image_info():
            x0,iy0,x1,iy1=im['bbox']
            if iy0>=top-8 and iy0<=bottom+60:
                imgs.append((idx,(x0,iy0,x1,iy1)))
        if nxt is not None: break
        top=48
    return labels, imgs

def pair(labels, imgs):
    res={}
    for L,(idx,lb) in labels.items():
        lx0,ly0,lx1,ly1=lb
        best=None
        for pi2,b in imgs:
            if pi2!=idx: continue
            ix0,iy0,ix1,iy1=b
            ov=min(lx1,ix1)-max(lx0,ix0)
            if ov<=0: continue
            if iy1<=ly0+2: gap=ly0-iy1          # image above label
            elif iy0>=ly1-2: gap=iy0-ly1          # image below label
            else: gap=0
            if gap< -3 or gap>160: continue
            sc=(ov,-abs(gap))
            if best is None or sc>best[0]: best=(sc,b)
        if best:
            b=best[1]
            u=(min(lx0,b[0]),min(ly0,b[1]),max(lx1,b[2]),max(ly1,b[3]))
            res[L]=(idx,u)
    return res

def crop(doc,res,qid,prefix="q"):
    out={}
    for L,(idx,b) in res.items():
        page=doc[idx]
        clip=pymupdf.Rect(max(0,b[0]-4),max(0,b[1]-4),min(page.rect.x1,b[2]+4),min(page.rect.y1,b[3]+4))
        out[L]=page.get_pixmap(clip=clip,dpi=220)
    return out

def sheet(qid, out):
    tiles=[]
    for L in "ABCD":
        if L not in out: continue
        im=Image.open(io.BytesIO(out[L].tobytes("png"))).convert("RGB")
        d=ImageDraw.Draw(im); d.rectangle([0,0,im.width-1,im.height-1],outline="red",width=3)
        d.text((5,5),L,fill="red")
        tiles.append(im)
    if not tiles: return None
    W=sum(t.width for t in tiles)+10*(len(tiles)+1)
    H=max(t.height for t in tiles)+20
    cv=Image.new("RGB",(W,H),"white"); xx=10
    for t in tiles: cv.paste(t,(xx,10)); xx+=t.width+10
    fn=os.path.join(STAGE,f"q{qid}_sheet.png"); cv.save(fn); return fn

if __name__=="__main__":
    Q=json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))
    Qd={q['id']:q for q in Q}
    dubs={"PUB":pymupdf.open(PUB),"PRO":pymupdf.open(PRO)}
    TARGETS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1262,1292,1147,1160,1588,1626,2002,1987,1988]
    for qid in TARGETS:
        q=Qd[qid]
        done=False
        for tag,doc in dubs.items():
            pi,y0=find_marker(doc,q['year'],q['yearQnum'])
            if pi is None: continue
            labels,imgs=collect(doc,pi,y0)
            res=pair(labels,imgs)
            if res:
                out=crop(doc,res,qid)
                fn=sheet(qid,out)
                print(f"id{qid} {tag} {q['year']}-{q['yearQnum']} opts={sorted(out.keys())} {os.path.basename(fn) if fn else ''}")
                done=True; break
        if not done:
            print(f"id{qid} nolabels")
