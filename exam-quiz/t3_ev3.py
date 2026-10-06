# -*- coding: utf-8 -*-
"""T3 取证3: id=42/39 解析高裁图 + id=280 周边块文本"""
import os, re, io, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
P = os.path.join(ROOT, '题目和答案pdf')
BK = os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf')
OUTD = os.path.join(ROOT, '_t3')
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
doc = pymupdf.open(BK)
CJK = re.compile(r'[' + chr(0x4e00) + '-' + chr(0x9fff) + ']{4,}')
log = io.open(os.path.join(ROOT, '_t3_ev3.txt'), 'w', encoding='utf-8')


def flat(s):
    return re.sub(r'\s+', '', s)


def blocks_of(pno):
    pg = doc[pno]
    return pg, sorted([b for b in pg.get_text('blocks') if b[4].strip()], key=lambda b: b[1])


for tid, extra in ((42, 260), (39, 260), (43, 200), (161, 200)):
    q = byid[tid]
    t = str(q.get('analysis') or '')
    probes = sorted(CJK.findall(re.sub(r'[$][^$]*[$]', ' ', t)), key=len, reverse=True)[:4]
    hits = [p for p in range(doc.page_count) if probes and probes[0] in flat(doc[p].get_text())]
    log.write('===== id=%d probes=%s hits=%s\n' % (tid, probes[:2], hits[:4]))
    if not hits:
        continue
    pno = hits[0]
    pg, bs = blocks_of(pno)
    bi = None
    for i, b in enumerate(bs):
        if probes[0] in flat(b[4]):
            bi = i
            break
    if bi is None:
        log.write('   !! block not found\n')
        continue
    y0 = max(0, bs[bi][1] - 40)
    y1 = min(pg.rect.height, bs[bi][3] + extra)
    pix = pg.get_pixmap(clip=pymupdf.Rect(70, y0, pg.rect.width - 50, y1), dpi=380)
    fn = os.path.join(OUTD, 'ev%04d.png' % tid)
    pix.save(fn)
    log.write('   p%d b%d -> %s\n' % (pno, bi, os.path.basename(fn)))
    for j in range(max(0, bi - 1), min(len(bs), bi + 8)):
        log.write('   [%d] %s\n' % (j, bs[j][4].replace('\n', ' ')[:260]))

# id=280 周边块
q = byid[280]
t = str(q.get('analysis') or '')
probes = sorted(CJK.findall(re.sub(r'[$][^$]*[$]', ' ', t)), key=len, reverse=True)[:3]
hits = [p for p in range(doc.page_count) if probes and probes[0] in flat(doc[p].get_text())]
log.write('===== id=280 hits=%s\n' % hits[:3])
if hits:
    pg, bs = blocks_of(hits[0])
    bi = None
    for i, b in enumerate(bs):
        if probes[0] in flat(b[4]):
            bi = i
            break
    for j in range(max(0, bi - 1), min(len(bs), bi + 12)):
        log.write('   [%d] %s\n' % (j, bs[j][4].replace('\n', ' ')[:260]))
log.close()
print('ok')
