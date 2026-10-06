# -*- coding: utf-8 -*-
"""Auto-crop option figures from the exam PDF.

For each broken question we know: pdf page(s), the option region, layout, count.
Render region at 4x, auto-detect whitespace gaps, split into N cells, save PNG.
"""
import sys, os, pymupdf
from PIL import Image
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')

D = r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ = os.path.join(D, "公共基础分类版真题详解（13~24）_题目.pdf")
PROQ = os.path.join(D, "岩土专业基础分类真题解析（16~24）_题目.pdf")
OUT = r"C:\Users\Administrator\.qclaw\workspace\autocrop"
os.makedirs(OUT, exist_ok=True)
pub = pymupdf.open(PUBQ)

def render(page, rect, scale=4):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=pymupdf.Rect(*rect))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return img

def gaps(profile, thr=0.985):
    """return list of (start,end) index ranges that are blank"""
    n = len(profile)
    mx = profile.max() if profile.max() > 0 else 1
    blank = profile < mx * (1 - thr) * -1  # placeholder
    blank = profile <= max(1, int(mx*0.02))
    runs = []
    s = None
    for i, b in enumerate(blank):
        if b and s is None: s = i
        if not b and s is not None: runs.append((s, i)); s = None
    if s is not None: runs.append((s, n))
    return runs

def split_cells(region_rect, layout, n=4):
    page = pub
    img = render(page, region_rect, scale=4)
    W, H = img.size
    a = np.asarray(img.convert("L"))
    dark = (a < 200).astype(np.int32)
    if layout == 'row':
        prof = dark.sum(axis=0); nr, nc = 1, n
    elif layout == 'col':
        prof = dark.sum(axis=1); nr, nc = n, 1
    elif layout == '2x2':
        # split horizontally first using row profile at mid
        rows = dark.sum(axis=1)
        mid = H//2
        # find blank band near mid
        best=None
        for y in range(int(H*0.25), int(H*0.75)):
            if rows[y] < max(1, rows.max()*0.02):
                best=y; break
        if best is None: best=mid
        top = dark[:best].sum(axis=0); bot = dark[best:].sum(axis=1).size
        # columns for each half
        cells=[]
        for (y0,y1,prof2) in [(0,best,dark[:best].sum(axis=0)),(best,H,dark[best:].sum(axis=0))]:
            # find 2 columns: split at blank near middle
            w=prof2.size; m2=w//2; b2=None
            for x in range(int(w*0.3), int(w*0.7)):
                if prof2[x] < max(1,prof2.max()*0.02): b2=x; break
            if b2 is None: b2=m2
            cells.append((0,b2,y0,y1)); cells.append((b2,w,y0,y1))
        return [(img.crop(c), c) for c in cells]
    # generic 1-D split
    gs = [(s,e) for (s,e) in gaps(prof) if s>2 and e < len(prof)-2]
    # cumulative content boundaries
    content = [(s,e) for (s,e) in gaps(prof, thr=0.94) ]
    # fallback: even split
    edges=[0]
    for k in range(1,nc):
        edges.append(int(len(prof)*k/nc))
    edges.append(len(prof))
    cells=[]
    if layout=='row':
        for k in range(nc):
            c=(edges[k],0,edges[k+1],H); cells.append((img.crop(c),c))
    else:
        for k in range(nr):
            c=(0,edges[k],W,edges[k+1]); cells.append((img.crop(c),c))
    return cells

# job: qid, [(page,rect,layout)] possibly multi-page, letterorder
JOBS = {
 306:  [(147,(83,548,480,714),'row2')],
 666:  [(151,(88,80,478,190),'2x2')],
 904:  [(153,(88,178,460,272),'2x2')],
 908:  [(167,(150,300,420,445),'row')],
 784:  [(151,(100,560,492,652),'row')],
 1040: [(201,(80,455,400,706),'2x2')],
 1262: [(143,(228,315,366,440),'row2')],
 1292: [(247,(80,415,500,625),'2x2')],
 812:  [(159,(82,238,478,352),'row')],
 669:  [(166,(150,398,450,600),'row')],
 693:  [(243,(85,255,510,340),'row')],
}
for qid, items in JOBS.items():
    for (p,rect,lay) in items:
        img=render(pub[p-1], rect, scale=4)
        img.save(os.path.join(OUT, f"id{qid}_p{p}_{lay}_full.png"))
print("rendered full regions")
