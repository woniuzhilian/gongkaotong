# -*- coding: utf-8 -*-
"""T3 取证2：导出 7 道 Theta 题的完整字段文本 + 重新裁取 id=160 的更高图"""
import os, re, io, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
OUT = io.open(os.path.join(ROOT, '_t3_theta2.txt'), 'w', encoding='utf-8')
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
BS = chr(92)
TH = BS + 'Theta'

for tid in (39, 42, 43, 160, 161, 278, 280):
    q = byid[tid]
    OUT.write('#' * 70 + '\n')
    OUT.write('id=%d yearQnum=%s region=%s\n' % (tid, q.get('yearQnum'), q.get('region')))
    for f in ('question', 'A', 'B', 'C', 'D', 'analysis'):
        t = str(q.get(f) or '')
        if TH in t:
            OUT.write('--- [%s] 含 %d 处 Theta ---\n' % (f, t.count(TH)))
            OUT.write(t + '\n')
OUT.write('#' * 70 + '\n')
for tid in (39, 42, 43, 160, 161, 278, 280):
    q = byid[tid]
    OUT.write('=== id=%d analysis 全文 ===\n%s\n\n' % (tid, q.get('analysis')))
OUT.close()

# 重新裁取 id=160 的解析块（更高）
P = os.path.join(ROOT, '题目和答案pdf')
BK = os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf')
doc = pymupdf.open(BK)
CJK = re.compile(r'[' + chr(0x4e00) + '-' + chr(0x9fff) + ']{4,}')


def flat(s):
    return re.sub(r'\s+', '', s)


q = byid[280]
t = str(q.get('analysis') or '')
probes = sorted(CJK.findall(re.sub(r'[$][^$]*[$]', ' ', t)), key=len, reverse=True)[:3]
hits = []
for pno in range(doc.page_count):
    pt = flat(doc[pno].get_text())
    if probes and probes[0] in pt:
        hits.append(pno)
log = io.open(os.path.join(ROOT, '_t3_theta3.txt'), 'w', encoding='utf-8')
log.write('探针=%s 命中页=%s\n' % (probes[:2], hits[:5]))
for pno in hits[:2]:
    pg = doc[pno]
    bs = sorted([b for b in pg.get_text('blocks') if b[4].strip()], key=lambda b: b[1])
    for bi, b in enumerate(bs):
        if probes[0] in flat(b[4]):
            y0 = max(0, b[1] - 30)
            y1 = min(pg.rect.height, b[3] + 430)
            pix = pg.get_pixmap(clip=pymupdf.Rect(70, y0, pg.rect.width - 50, y1), dpi=400)
            fn = os.path.join(ROOT, '_t3', 'th0280_tall.png')
            pix.save(fn)
            log.write('p%d b%d y=%s..%s -> %s\n文本: %s\n' % (
                pno, bi, round(y0, 1), round(y1, 1), os.path.basename(fn),
                b[4].replace('\n', ' ')[:400]))
            # 后续块的纯文本
            for nb in bs[bi + 1:bi + 4]:
                log.write('  下一块: %s\n' % nb[4].replace('\n', ' ')[:300])
            break
log.close()
print('done')
