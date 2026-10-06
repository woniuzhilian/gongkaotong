# -*- coding: utf-8 -*-
"""Render each target question's FULL block (marker -> next marker, across page breaks) to one stacked PNG."""
import sys, os, re, json, pymupdf
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
OUT=r"C:\Users\Administrator\.qclaw\workspace\qblocks2"
os.makedirs(OUT, exist_ok=True)
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
PRO=os.path.join(PDFDIR,"岩土专业基础历年真题试题册（2024版）.pdf")
qs=json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))
Q={q['id']:q for q in qs}
MK=re.compile(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】')

def marker_of(q):
    y=q['year']; n=q['yearQnum']
    return (y,n)

def find_marker(doc, y, n):
    pats=[re.compile(r'【\s*'+str(y)+r'\s*补?\s*[-–]\s*'+str(n)+r'\s*】')]
    for i in range(len(doc)):
        t=doc[i].get_text()
        for p in pats:
            m=p.search(t)
            if m: return i, m.start(), m.end()
    return None

def page_rect_y(page, start_char, end_char):
    # map char offsets -> y using rawdict spans
    # simpler: use text blocks
    d=page.get_text("dict")
    return None

def crop_page(page, y0, y1, dpi=170):
    clip=pymupdf.Rect(20, y0, page.rect.x1-20, min(y1, page.rect.y1-15))
    if clip.y1-clip.y0 < 8: return None
    return page.get_pixmap(clip=clip, dpi=dpi)

def render(qid):
    q=Q[qid]; y,n=q['year'],q['yearQnum']
    for path,doc in (("PUB",pymupdf.open(PUB)),("PRO",pymupdf.open(PRO))):
        r=find_marker(doc, y, n)
        if not r: continue
        pi,cs,ce=r
        # find y of marker on that page via search_for text
        page=doc[pi]
        rects=page.search_for(re.search(r'【\s*\d{4}[^】]*】', page.get_text()[cs:cs+20]).group(0)) if False else None
        # locate marker y by scanning words for the marker token
        y0=None
        for w in page.get_text("words"):
            if re.fullmatch(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】', w[4]):
                if (str(y) in w[4]) and (re.search(r'[-–]\s*'+str(n)+r'\s*】', w[4])):
                    y0=w[1]-6; break
        if y0 is None:
            # fallback: any marker line
            y0=60
        # find next marker on same or next pages
        imgs=[]
        pagea=page; ya=y0
        for step in range(0,3):
            if pi+step>=len(doc): break
            pg=doc[pi+step]
            # next marker y on this page after ya
            nxt=None
            for w in pg.get_text("words"):
                if re.fullmatch(r'【\s*\d{4}\s*补?\s*[-–]\s*\d+\s*】', w[4]) and (w[1] > ya+5 if step==0 else w[1]>100):
                    nxt=w[1]-6; break
            if nxt is not None:
                pm=crop_page(pg, ya, nxt); 
                if pm: imgs.append(pm)
                break
            else:
                pm=crop_page(pg, ya, pg.rect.y1-15)
                if pm: imgs.append(pm)
                ya=60  # top of next page
        if not imgs: 
            print(f"id{qid} {path} no crop"); return
        # stack
        tiles=[Image.open(__import__('io').BytesIO(p.tobytes("png"))) for p in imgs]
        W=max(t.width for t in tiles); H=sum(t.height for t in tiles)+10*(len(tiles)-1)
        canvas=Image.new("RGB",(W,H),"white"); yy=0
        for t in tiles:
            canvas.paste(t,(0,yy)); yy+=t.height+10
        fn=os.path.join(OUT,f"q{qid}.png"); canvas.save(fn)
        print(f"id{qid} {path} page{pi+1} -> {os.path.basename(fn)} {W}x{H} pages={len(tiles)}")
        return
    print(f"id{qid} NOTFOUND")

TARGETS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002,1987,1988,840,694,815,1175]
for t in TARGETS: render(t)
