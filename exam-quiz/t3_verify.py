# -*- coding: utf-8 -*-
"""T3 取证：按探针在题目册/解析册里定位并裁图，核对 sigma / varepsilon / ominus 三种字形"""
import os, re, io, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
BOOK = {
    'q': os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf'),
    'a': os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf'),
}
OUTD = os.path.join(ROOT, '_t3')
os.makedirs(OUTD, exist_ok=True)
log = io.open(os.path.join(ROOT, '_t3_verify.txt'), 'w', encoding='utf-8')

JOBS = [
    ('id39-题干E-Theta', 'q', ['已知', 'Fe'], 3),
    ('id25-解析-epsilon', 'a', ['平均平动动能'], 0),
    ('id67-解析-varsigma', 'a', ['第三强度理论'], 0),
]

docs = {}
for name, which, probes, _ in JOBS:
    if which not in docs:
        docs[which] = pymupdf.open(BOOK[which])

for name, which, probes, nth in JOBS:
    doc = docs[which]
    found = []
    for pno in range(doc.page_count):
        txt = re.sub(r'\s+', '', doc[pno].get_text())
        score = sum(1 for x in probes if re.sub(r'\s+', '', x) in txt)
        if score >= len(probes):
            found.append(pno)
    log.write('== %s 命中页(0-based)=%s\n' % (name, found[:6]))
    if not found:
        continue
    pno = found[nth] if nth < len(found) else found[0]
    pg = doc[pno]
    bs = [b for b in pg.get_text('blocks') if b[4].strip()]
    bs.sort(key=lambda b: b[1])
    tgt = None
    for i, b in enumerate(bs):
        flat = re.sub(r'\s+', '', b[4])
        if any(re.sub(r'\s+', '', x) in flat for x in probes):
            tgt = b
            break
    if tgt is None:
        log.write('   未找到块\n')
        continue
    y0 = max(0, tgt[1] - 26)
    y1 = min(pg.rect.height, tgt[3] + 66)
    r = pymupdf.Rect(70, y0, pg.rect.width - 50, y1)
    pix = pg.get_pixmap(clip=r, dpi=400)
    fn = os.path.join(OUTD, name + '.png')
    pix.save(fn)
    log.write('   p%d y=%s..%s -> %s (%dx%d)\n' % (pno, round(y0, 1), round(y1, 1), fn, pix.width, pix.height))
    log.write('   块文本: %s\n' % tgt[4].replace('\n', ' ')[:220])
log.close()
print('done')
