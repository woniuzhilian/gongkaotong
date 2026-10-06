"""按题干中文文本在分类版题目册中定位每题真实位置，再回溯其上方的【年-号】标记"""
import os, re, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
OUTD = os.path.join(ROOT, '_t1')
log = open(os.path.join(ROOT, '_t1_locate.txt'), 'w', encoding='utf-8')
def p(*a): print(*a, file=log)

IDS = [8,12,17,61,131,136,167,207,253,256,267,318,326,371,376,380,
       383,413,492,501,521,615,617,623,684,731,735,737,855,856,863,
       971,973,976,1020,1095,1103,1122,1140,1214,1217,1280,1294,1336,
       1372,1375,1380,1410]
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}

CJK = re.compile(r'[一-鿿]{6,}')
def probe(txt):
    t = re.sub(r'\$[^$]*\$', ' ', txt or '')
    t = re.sub(r'<br>|<img[^>]*>', ' ', t)
    runs = CJK.findall(t)
    runs.sort(key=len, reverse=True)
    return runs[0][:14] if runs else ''

MARK = re.compile(r'【\s*(\d{4})\s*(补)?\s*[-–]\s*(\d+)\s*】')
doc = pymupdf.open(os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf'))
pages = []
for pno in range(doc.page_count):
    pg = doc[pno]
    blocks = [b for b in pg.get_text('blocks') if b[4].strip()]
    raw = re.sub(r'\s+', '', pg.get_text())
    pages.append((pg, blocks, raw))

def norm(s):
    return re.sub(r'\s+', '', s)

res = {}
for tid in IDS:
    q = byid[tid]
    key_db = '%s-%s' % (q['year'], q['yearQnum'])
    pr = probe(q['question'])
    hit = None
    if pr:
        for pno, (pg, blocks, raw) in enumerate(pages):
            i = raw.find(norm(pr))
            if i < 0:
                continue
            # 找到包含该文本的 block，再回溯其上最近的标记 block
            by = None
            for b in blocks:
                if norm(pr) in norm(b[4]):
                    by = b[1]; break
            if by is None:
                by = 40
            cands = []
            for b in blocks:
                m = MARK.search(b[4])
                if m and b[1] <= by + 2:
                    cands.append((b[1], m.group(1) + ('补' if m.group(2) else '') + '-' + str(int(m.group(3)))))
            cands.sort()
            mk = cands[-1][1] if cands else '?'
            hit = (pno, by, mk, pr)
            break
    res[tid] = hit
    if hit is None:
        p('id=%-5s %-10s 未定位  probe=%r' % (tid, key_db, pr))
    else:
        pno, by, mk, pr = hit
        flag = 'OK ' if mk == key_db else '!! '
        p('%sid=%-5s db=%-10s 书=%-10s p%-4d y%3d  probe=%s' % (flag, tid, key_db, mk, pno, by, pr))

# 用定位结果重裁
if not os.path.isdir(OUTD): os.mkdir(OUTD)
p('\n--- 重裁 ---')
for tid in IDS:
    hit = res.get(tid)
    if not hit: continue
    pno, by, mk, pr = hit
    pg, blocks, raw = pages[pno]
    ys = sorted(b[1] for b in blocks if MARK.search(b[4]) and b[1] <= by + 2)
    y0 = ys[-1] if ys else max(0, by - 5)
    nxt = sorted(b[1] for b in blocks if MARK.search(b[4]) and b[1] > y0 + 5)
    y1 = nxt[0] if nxt else pg.rect.y1
    clip = pymupdf.Rect(60, max(0, y0 - 3), pg.rect.x1 - 20, min(pg.rect.y1, y1 - 3))
    pix = pg.get_pixmap(clip=clip, dpi=200)
    fn = 'r%04d_%s.png' % (tid, mk.replace('-', '_'))
    pix.save(os.path.join(OUTD, fn))
    line = 'id=%-5s %-10s p%-4d y(%3d,%3d) -> %s %dx%d' % (tid, mk, pno, y0, y1, fn, pix.width, pix.height)
    if y1 >= pg.rect.y1 - 1:
        line += '  [跨页,需续页]'
    p(line)
doc.close(); log.close()
print('done')
