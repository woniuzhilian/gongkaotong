# -*- coding: utf-8 -*-
"""T3 取证：对指定 (id,字段) 用其最长中文串在相应册子里定位并裁图"""
import os, re, io, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
BOOK = {
    'question': os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf'),
    'other': os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf'),
}
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
OUTD = os.path.join(ROOT, '_t3')
os.makedirs(OUTD, exist_ok=True)
log = io.open(os.path.join(ROOT, '_t3_theta.txt'), 'w', encoding='utf-8')
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
CJK = re.compile(r'[' + chr(0x4e00) + '-' + chr(0x9fff) + ']{4,}')


def flat(s):
    return re.sub(r'\s+', '', s)


JOBS = [(39, 'question'), (42, 'analysis'), (43, 'analysis'), (160, 'analysis'),
        (161, 'analysis'), (278, 'question'), (280, 'analysis')]

docs = {}
for tid, f in JOBS:
    q = byid[tid]
    t = str(q.get(f) or '')
    key = 'question' if f == 'question' else 'other'
    if key not in docs:
        docs[key] = pymupdf.open(BOOK[key])
    doc = docs[key]
    probes = sorted(CJK.findall(re.sub(r'[$][^$]*[$]', ' ', t)), key=len, reverse=True)[:3]
    if not probes:
        probes = sorted(CJK.findall(t), key=len, reverse=True)[:3]
    hit_pages = []
    for pno in range(doc.page_count):
        pt = flat(doc[pno].get_text())
        if probes and probes[0] in pt:
            hit_pages.append(pno)
    log.write('== id=%d %s 探针=%s 命中页=%s\n' % (tid, f, probes[:2], hit_pages[:5]))
    if not hit_pages:
        continue
    done = False
    for pno in hit_pages[:3]:
        pg = doc[pno]
        bs = sorted([b for b in pg.get_text('blocks') if b[4].strip()], key=lambda b: b[1])
        for b in bs:
            if probes[0] in flat(b[4]):
                y0 = max(0, b[1] - 30)
                y1 = min(pg.rect.height, b[3] + 78)
                pix = pg.get_pixmap(clip=pymupdf.Rect(70, y0, pg.rect.width - 50, y1), dpi=400)
                fn = os.path.join(OUTD, 'th%04d_%s.png' % (tid, f[:4]))
                pix.save(fn)
                log.write('   p%d y=%s..%s -> %s\n      文本: %s\n' % (
                    pno, round(y0, 1), round(y1, 1), os.path.basename(fn),
                    b[4].replace('\n', ' ')[:200]))
                done = True
                break
        if done:
            break
    if not done:
        log.write('   !! 未定位到块\n')
log.close()
print('done')
