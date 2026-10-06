# -*- coding: utf-8 -*-
import sys, os, re, json, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
ANYMK=re.compile(r'【\s*(\d{4})\s*(补?)\s*[-–]\s*(\d+)\s*】')
def norm(s):
    s=re.sub(r'<[^>]+>','',str(s)); s=re.sub(r'\{[^}]*\}','',s)
    s=s.replace('$','')
    s=re.sub(r'\\([A-Za-z]+)',r'\1',s)
    return ''.join(ch for ch in s if '\u4e00'<=ch<='\u9fff' or ch.isalnum())
doc=pymupdf.open(PUB)
Q={q['id']:q for q in json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))}

def locate(probe):
    for i in range(len(doc)):
        t=doc[i].get_text()
        if probe in norm(t):
            return i
    return None

def dump(qid):
    q=Q[qid]; raw=re.sub(r'<[^>]+>','',q['question'])
    pi=None
    for L in (24,16,12,8):
        nr=norm(raw)
        if len(nr)>=L:
            pi=locate(nr[:L])
            if pi is not None: break
    if pi is None: print(f"id{qid} NOLOC"); return
    page=doc[pi]
    print(f"===== id{qid} page{pi+1} rect={page.rect}")
    for w in page.get_text("words"):
        mm=re.search(r'[（(【]([A-D]?\d*)[）)】]', w[4]) or ANYMK.search(w[4])
        if mm:
            print(f"  W ({w[0]:.0f},{w[1]:.0f},{w[2]:.0f},{w[3]:.0f}) {w[4]!r}")
    for im in page.get_image_info():
        b=im['bbox']
        print(f"  IMG ({b[0]:.0f},{b[1]:.0f},{b[2]:.0f},{b[3]:.0f}) {im['width']}x{im['height']}")
    # drawings (vector) count and bbox range
    ds=page.get_drawings()
    if ds:
        xs0=min(d['rect'].x0 for d in ds); ys0=min(d['rect'].y0 for d in ds)
        xs1=max(d['rect'].x1 for d in ds); ys1=max(d['rect'].y1 for d in ds)
        print(f"  DRAW n={len(ds)} bbox=({xs0:.0f},{ys0:.0f},{xs1:.0f},{ys1:.0f})")

for qid in [306,447,538,658,666,669,784,904,928,1040,1147,1160,1262,1292]:
    dump(qid)
