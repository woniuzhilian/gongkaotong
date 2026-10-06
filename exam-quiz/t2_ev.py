# -*- coding: utf-8 -*-
"""T3 取证4: cdots 单位题干的原文裁图 (题目册)"""
import os, re, io, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
P = os.path.join(ROOT, '题目和答案pdf')
BK = os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf')
OUTD = os.path.join(ROOT, '_t3')
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
doc = pymupdf.open(BK)
CJK = re.compile(r'[' + chr(0x4e00) + '-' + chr(0x9fff) + ']{4,}')
log = io.open(os.path.join(ROOT, '_t3_ev4.txt'), 'w', encoding='utf-8')


def flat(s):
    return re.sub(r'\s+', '', s)


for tid in (53, 9, 384):
    q = byid[tid]
    t = str(q.get('question') or '')
    probes = sorted(CJK.findall(re.sub(r'[$][^$]*[$]', ' ', t)), key=len, reverse=True)[:4]
    hits = [p for p in range(doc.page_count) if probes and probes[0] in flat(doc[p].get_text())]
    log.write('===== id=%d probes=%s hits=%s\n' % (tid, probes[:2], hits[:4]))
    if not hits:
        continue
    pg = doc[hits[0]]
    bs = sorted([b for b in pg.get_text('blocks') if b[4].strip()], key=lambda b: b[1])
    for i, b in enumerate(bs):
        if probes[0] in flat(b[4]):
            y0 = max(0, b[1] - 40)
            y1 = min(pg.rect.height, b[3] + 300)
            pix = pg.get_pixmap(clip=pymupdf.Rect(70, y0, pg.rect.width - 50, y1), dpi=380)
            fn = 'cd%04d.png' % tid
            pix.save(os.path.join(OUTD, fn))
            log.write('   p%d b%d -> %s\n' % (hits[0], i, fn))
            for j in range(i, min(len(bs), i + 5)):
                log.write('   [%d] %s\n' % (j, bs[j][4].replace('\n', ' ')[:240]))
            break
log.close()
print('ok')
