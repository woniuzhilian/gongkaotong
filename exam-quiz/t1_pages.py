"""为 48 道题干/选项侧 T1 题目，从 公共基础分类版题目册 裁出各自的题目区域图"""
import os, re, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
OUTD = os.path.join(ROOT, '_t1')
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
log = open(os.path.join(ROOT, '_t1_pages.txt'), 'w', encoding='utf-8')


def p(*a):
    print(*a, file=log)


if not os.path.isdir(OUTD):
    os.mkdir(OUTD)

IDS = [8, 12, 17, 61, 131, 136, 167, 207, 253, 256, 267, 318, 326, 371, 376, 380,
       383, 413, 492, 501, 521, 615, 617, 623, 684, 731, 735, 737, 855, 856, 863,
       971, 973, 976, 1020, 1095, 1103, 1122, 1140, 1214, 1217, 1280, 1294, 1336,
       1372, 1375, 1380, 1410]
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}

MARK = re.compile(r'【\s*(\d{4})\s*(补)?\s*[-–]\s*(\d+)\s*】')
doc = pymupdf.open(os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf'))

# 建立 索引: "2013-8" / "2022补-16" -> (页号, 该题起始y, 页宽矩形)
index = {}
for pno in range(doc.page_count):
    pg = doc[pno]
    blocks = [b for b in pg.get_text('blocks') if b[4].strip()]
    found = []
    for b in blocks:
        m = MARK.search(b[4])
        if m:
            key = m.group(1) + ('补' if m.group(2) else '') + '-' + str(int(m.group(3)))
            found.append((key, b[1], b[0]))
    found.sort(key=lambda x: x[1])
    for i, (key, y0, x0) in enumerate(found):
        y1 = found[i + 1][1] if i + 1 < len(found) else pg.rect.y1
        index[key] = (pno, y0, y1, x0)

p('索引到 %d 个题号标记' % len(index))

missing = []
jobs = []
for tid in IDS:
    q = byid[tid]
    key = '%s-%s' % (q['year'], q['yearQnum'])
    if key not in index:
        missing.append((tid, key))
        continue
    jobs.append((tid, key) + index[key])

p('命中 %d 题, 未命中 %d 题' % (len(jobs), len(missing)))
for tid, key in missing:
    p('  未命中 id=%s key=%s' % (tid, key))

p('\n--- 裁图 ---')
order = sorted(index.items(), key=lambda kv: (kv[1][0], kv[1][1]))
pos = {k: i for i, (k, _) in enumerate(order)}
BOTTOM = pymupdf.Rect(0, 0, 0, 0)
for tid, key, pno, y0, y1, x0 in jobs:
    pg = doc[pno]
    clip = pymupdf.Rect(60, max(0, y0 - 3), pg.rect.x1 - 20, min(pg.rect.y1, y1 - 3))
    pix = pg.get_pixmap(clip=clip, dpi=200)
    fn = 'q%04d_%s.png' % (tid, key.replace('-', '_'))
    pix.save(os.path.join(OUTD, fn))
    p('id=%-5s %-12s p%-4d y(%3d,%3d) -> %s  %dx%d' % (tid, key, pno, y0, y1, fn, pix.width, pix.height))
    if y1 >= pg.rect.y1 - 1:
        nxt = order[pos[key] + 1] if pos[key] + 1 < len(order) else None
        if nxt:
            npg = doc[nxt[1][0]]
            c2 = pymupdf.Rect(60, 0, npg.rect.x1 - 20, max(60, nxt[1][1] - 3))
            pz = npg.get_pixmap(clip=c2, dpi=200)
            f2 = 'q%04d_%s_b.png' % (tid, key.replace('-', '_'))
            pz.save(os.path.join(OUTD, f2))
            p('      续页 -> %s  %dx%d (接 %s)' % (f2, pz.width, pz.height, nxt[0]))

# 同一页被多题复用的情况提示
from collections import Counter
c = Counter(j[2] for j in jobs)
p('\n涉及页数: %d' % len(c))
doc.close()
log.close()
print('jobs=%d missing=%d' % (len(jobs), len(missing)))
