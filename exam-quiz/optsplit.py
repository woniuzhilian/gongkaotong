# -*- coding: utf-8 -*-
import sys, os, re, json, io, pymupdf
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
PRO=os.path.join(PDFDIR,"岩土专业基础历年真题试题册（2024版）.pdf")
OUT=r"C:\Users\Administrator\.qclaw\workspace\optsplit"; os.makedirs(OUT,exist_ok=True)
BAND=r"C:\Users\Administrator\.qclaw\workspace\bands"; os.makedirs(BAND,exist_ok=True)
ANY=re.compile(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】')
PRONUM=re.compile(r'(?m)^\s*(\d{1,3})\s*[、.]')
LBL=re.compile(r'[（(]([A-D])[）)]')
def norm(s):
    s=re.sub(r'<[^>]+>','',str(s)); s=re.sub(r'\{[^}]*\}','',s); s=s.replace('$','').replace('\\','')
    return ''.join(ch for ch in s if '\u4e00'<=ch<='\u9fff' or ch.isalnum())
DOCS={"pub":pymupdf.open(PUB),"pro":pymupdf.open(PRO)}
Q={q['id']:q for q in json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))}
def locate(doc,probe):
    for i in range(len(doc)):
        if probe in norm(doc[i].get_text()): return i
    return None
def find_region(doc,pi,kind,probe):
    t=doc[pi].get_text(); nt=norm(t); j=nt.find(probe); k=0; idx=0
    for idx,ch in enumerate(t):
        if '\u4e00'<=ch<='\u9fff' or ch.isalnum(): k+=1
        if k>=j+1: break
    start=idx
    if kind=="pub":
        m=ANY.search(t,start); end=m.start() if m else len(t)
    else:
        end=len(t)
        for mm in PRONUM.finditer(t):
            if mm.start()>start: end=mm.start(); break
    return start,end
def stem_y(page, start):
    # y of the word whose char offset == start (the stem start)
    txt=page.get_text()
    k=0; pos=0
    for i,ch in enumerate(txt):
        if '\u4e00'<=ch<='\u9fff' or ch.isalnum(): k+=1
        if k>=start: pos=i; break
    y=0.0
    for w in page.get_text("words"):
        p=txt.find(w[4])
        if p<=pos: y=max(y,w[1])
    return y

def get_labels(page,start,end):
    y0=stem_y(page,start)
    tw=[(w[4],w) for w in page.get_text("words")]
    res={}
    for txt,w in tw:
        m=LBL.search(txt)
        if not m: continue
        if w[1] < y0+2: continue   # must be below stem start
        L=m.group(1)
        if L not in res: res[L]=w
    return res
def band_and_split(qid, page, labs, stemtop):
    if len(labs)<2: return None
    ytop=min(w[1] for w in labs.values())
    imgs=[im['bbox'] for im in page.get_image_info() if im['bbox'][1] < ytop+30 and im['bbox'][1] > stemtop-10]
    if imgs: ytop=min(ytop, min(b[1] for b in imgs))
    ybot=max(w[3] for w in labs.values())+6
    # split x: nearest gap between label x-centers
    cis=sorted(((w[0]+w[2])/2, L) for L,w in labs.items())
    cuts=[35]
    for a,b in zip(cis, cis[1:]): cuts.append((a[0]+b[0])/2)
    cuts.append(page.rect.x1-25)
    order=[L for _,L in cis]
    crops={}
    for i,L in enumerate(order):
        r=pymupdf.Rect(cuts[i], max(5,ytop-4), cuts[i+1], min(page.rect.y1-5, ybot))
        crops[L]=page.get_pixmap(clip=r, dpi=170)
    band=page.get_pixmap(clip=pymupdf.Rect(35, max(5,ytop-4), page.rect.x1-25, min(page.rect.y1-5,ybot)), dpi=150)
    return crops, band
def sheet(qid,crops):
    tiles=[]
    for L in "ABCD":
        if L not in crops: continue
        im=Image.open(io.BytesIO(crops[L].tobytes("png"))).convert("RGB")
        d=ImageDraw.Draw(im); d.rectangle([0,0,im.width-1,im.height-1],outline="red",width=3); d.text((5,5),L,fill="red")
        tiles.append(im)
    if not tiles: return None
    W=sum(t.width for t in tiles)+10*(len(tiles)+1); H=max(t.height for t in tiles)+20
    cv=Image.new("RGB",(W,H),"white"); xx=10
    for t in tiles: cv.paste(t,(xx,10)); xx+=t.width+10
    fn=os.path.join(OUT,f"q{qid}.png"); cv.save(fn); return fn
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292]
for qid in IDS:
    q=Q[qid]; nq=norm(re.sub(r'<[^>]+>','',q['question']))
    done=False
    for tag,kind in (("pub","pub"),("pro","pro")):
        doc=DOCS[tag]; pi=None
        for L in (26,20,14,10):
            if len(nq)>=L:
                pi=locate(doc,nq[:L])
                if pi is not None: break
        if pi is None: continue
        page=doc[pi]; start,end=find_region(doc,pi,kind,nq[:max(8,min(20,len(nq)))])
        labs=get_labels(page,start,end)
        r=band_and_split(qid,page,labs, page.rect.y0)
        if not r: print(f"id{qid} {tag} p{pi+1} labels={sorted(labs)} <2"); continue
        crops,band=r
        Image.open(io.BytesIO(band.tobytes("png"))).save(os.path.join(BAND,f"q{qid}.png"))
        fn=sheet(qid,crops)
        print(f"id{qid} {tag} p{pi+1} opts={sorted(crops)} -> {os.path.basename(fn)} band q{qid}.png")
        done=True; break
    if not done: print(f"id{qid} FAIL")
