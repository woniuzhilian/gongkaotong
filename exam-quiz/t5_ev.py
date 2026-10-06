# -*- coding: utf-8 -*-
"""#5 取证：把代表性题目的原书区块裁成图，逐一目视确认 : ; 的真实身份"""
import os, re, io, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
P = os.path.join(ROOT, '题目和答案pdf')
BK = os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf')
BKA = os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf')
OUTD = os.path.join(ROOT, '_t5')
if not os.path.isdir(OUTD):
    os.makedirs(OUTD)
data = json.load(io.open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
CJK = re.compile(r'[' + chr(0x4e00) + '-' + chr(0x9fff) + ']{4,}')
IDS = [2, 134, 363, 413, 607]
log = io.open(os.path.join(ROOT, '_t5_ev.txt'), 'w', encoding='utf-8', newline='\r\n')


def flat(s):
    return re.sub(r'\s+', '', s)


def probes_of(t):
    return sorted(CJK.findall(re.sub(r'[$][^$]*[$]', ' ', t)), key=len, reverse=True)[:4]


def crop(doc, tag, tid, text, above, below, wide):
    ps = probes_of(text)
    if not ps:
        log.write('   %s id=%d 无中文探针\n' % (tag, tid))
        return
    hits = [p for p in range(doc.page_count) if ps[0] in flat(doc[p].get_text())]
    log.write('   %s id=%d 探针=%s 命中页=%s\n' % (tag, tid, ps[:2], hits[:4]))
    if not hits:
        return
    pg = doc[hits[0]]
    bs = sorted([b for b in pg.get_text('blocks') if b[4].strip()], key=lambda b: b[1])
    for i, b in enumerate(bs):
        if ps[0] not in flat(b[4]):
            continue
        y0 = max(0, b[1] - above)
        y1 = min(pg.rect.height, b[3] + below)
        x0 = 70 if not wide else 40
        pix = pg.get_pixmap(clip=pymupdf.Rect(x0, y0, pg.rect.width - x0, y1), dpi=300)
        fn = '%s%04d.png' % (tag, tid)
        pix.save(os.path.join(OUTD, fn))
        log.write('   -> %s p%d 文本=%s\n' % (fn, hits[0], b[4].replace('\n', ' ')[:200]))
        for j in range(i + 1, min(len(bs), i + 4)):
            log.write('      下文%d: %s\n' % (j, bs[j][4].replace('\n', ' ')[:200]))
        return
    log.write('   未找到含探针的区块\n')


dq = pymupdf.open(BK)
da = pymupdf.open(BKA)
for tid in IDS:
    q = byid[tid]
    log.write('===== id=%d %s-%s\n' % (tid, q['year'], q['yearQnum']))
    crop(dq, 'q', tid, str(q.get('question') or ''), 30, 200, True)
    for f in ('A', 'B', 'C', 'D'):
        v = str(q.get(f) or '')
        if ';' in v or ':' in v:
            crop(dq, 'op' + f, tid, v, 20, 120, True)
    crop(da, 'an', tid, str(q.get('analysis') or ''), 30, 240, True)
dq.close()
da.close()
log.close()
print('ok')
