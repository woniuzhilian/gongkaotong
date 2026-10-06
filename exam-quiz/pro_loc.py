# -*- coding: utf-8 -*-
"""在《岩土专业基础历年真题解析册（2024版）》里按探针定位 7 道专业基础解析的原文"""
import os, re, io, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
PDF = os.path.join(P, '岩土专业基础历年真题解析册（2024版）.pdf')
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
OUT = io.open(os.path.join(ROOT, '_pro_loc.txt'), 'w', encoding='utf-8')

IDS = [1467, 1524, 1583, 1645, 1827, 1828, 1844]
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}

CJK = re.compile(r'[' + chr(0x4e00) + '-' + chr(0x9fff) + ']{5,}')
def norm(s):
    return re.sub(r'\s+', '', s)

doc = pymupdf.open(PDF)
PAGES = [norm(doc[i].get_text()) for i in range(doc.page_count)]

def probes(q):
    out = []
    for f in ['analysis', 'question']:
        t = re.sub(r'\$[^$]*\$', ' ', str(q.get(f) or ''))
        t = re.sub(r'<br>|<img[^>]*>', ' ', t)
        for r in CJK.findall(t):
            out.append(norm(r)[:12])
    seen, keep = set(), []
    for x in sorted(out, key=len, reverse=True):
        if x not in seen:
            seen.add(x); keep.append(x)
    return keep[:8]

for tid in IDS:
    q = byid[tid]
    ps = probes(q)
    scored = []
    for i, pt in enumerate(PAGES):
        s = sum(1 for x in ps if x in pt)
        if s:
            scored.append((s, i))
    scored.sort(reverse=True)
    OUT.write('==== id=%d 探针=%s\n' % (tid, ps[:4]))
    OUT.write('     命中页(0-based,得分)=%s\n' % scored[:4])
    if not scored:
        OUT.write('     !! 未命中\n')
        continue
    pno = scored[0][1]
    raw = doc[pno].get_text('blocks')
    raw = [b for b in raw if b[4].strip()]
    raw.sort(key=lambda b: b[1])
    hits = [b for b in raw if any(x in norm(b[4]) for x in ps)]
    for b in hits:
        OUT.write('  --- p%d y=%s..%s\n' % (pno, round(b[1], 1), round(b[3], 1)))
        OUT.write('  %s\n' % b[4].replace('\n', '⏎'))
OUT.close()
print('done')
