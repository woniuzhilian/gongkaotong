"""题干+选项多探针打分定位，并与【年-号】标记交叉校验，然后裁图"""
import os, re, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
OUTD = os.path.join(ROOT, '_t1')
log = open(os.path.join(ROOT, '_t1_loc2.txt'), 'w', encoding='utf-8')
def p(*a): print(*a, file=log)

IDS = [8,12,17,61,131,136,167,207,253,256,267,318,326,371,376,380,
       383,413,492,501,521,615,617,623,684,731,735,737,855,856,863,
       971,973,976,1020,1095,1103,1122,1140,1214,1217,1280,1294,1336,
       1372,1375,1380,1410]
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}

CJK = re.compile(r'[一-鿿]{4,}')
def probes(q):
    out = []
    for f in ['question', 'A', 'B', 'C', 'D']:
        t = re.sub(r'\$[^$]*\$', ' ', str(q.get(f) or ''))
        t = re.sub(r'<br>|<img[^>]*>', ' ', t)
        for r in CJK.findall(t):
            if len(r) >= 5:
                out.append(r[:16])
    seen, keep = set(), []
    for x in sorted(out, key=len, reverse=True):
        if x not in seen:
            seen.add(x); keep.append(x)
    return keep[:8]

def norm(s): return re.sub(r'\s+', '', s)
MARK = re.compile(r'【\s*(\d{4})\s*(补)?\s*[-–]\s*(\d+)\s*】')
doc = pymupdf.open(os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf'))
pages = []
for pno in range(doc.page_count):
    pg = doc[pno]
    blocks = [b for b in pg.get_text('blocks') if b[4].strip()]
    pages.append((pg, blocks, norm(pg.get_text())))

def markers_on(blocks):
    r = []
    for b in blocks:
        m = MARK.search(b[4])
        if m:
            r.append((b[1], m.group(1) + ('补' if m.group(2) else '') + '-' + str(int(m.group(3)))))
    r.sort()
    return r

def key_page_index():
    idx = {}
    for pno, (pg, blocks, raw) in enumerate(pages):
        for y, k in markers_on(blocks):
            idx.setdefault(k, (pno, y))
    return idx
KEYIDX = key_page_index()

report = []
for tid in IDS:
    q = byid[tid]
    key_db = '%s-%s' % (q['year'], q['yearQnum'])
    prs = probes(q)
    score = {}
    for i, pr in enumerate(prs):
        n = norm(pr)
        for pno, (_, _, raw) in enumerate(pages):
            if n in raw:
                score.setdefault(pno, []).append(i)
    cand = sorted(score, key=lambda x: (-len(score[x]), x))
    kp = KEYIDX.get(key_db, (None, None))[0]
    best = None
    if cand:
        # 若某候选页同时是 key 页或其相邻页，优先
        pref = [c for c in cand if kp is not None and abs(c - kp) <= 1]
        best = pref[0] if pref else cand[0]
    elif kp is not None:
        best = kp
    if best is None:
        report.append((tid, key_db, '?', 0, [], prs)); continue
    ys = [y for y, k in markers_on(pages[best][1]) if y <= pages[best][1][0][1] + 9e4]
    mk_here = [k for y, k in markers_on(pages[best][1])]
    # 该题在页内的起始 y：取 score 最高页中最早命中的探针 block 上方最近的标记
    top = min((b[1] for b in pages[best][1] if any(norm(x) in norm(b[4]) for x in prs)), default=None)
    above = [m for m in markers_on(pages[best][1]) if top is None or m[0] <= top + 2]
    mk = above[-1][1] if above else (mk_here[0] if mk_here else '?')
    y0 = above[-1][0] if above else (top or 40)
    nxt = [m[0] for m in markers_on(pages[best][1]) if m[0] > y0 + 5]
    y1 = nxt[0] if nxt else pages[best][0].rect.y1
    report.append((tid, key_db, mk, len(score[best]) if best in score else 0, cand[:3], prs[:4]))

    pg, blocks, raw = pages[best]
    clip = pymupdf.Rect(60, max(0, y0 - 3), pg.rect.x1 - 20, min(pg.rect.y1, y1 - 3))
    pix = pg.get_pixmap(clip=clip, dpi=200)
    fn = 'v%04d_%s.png' % (tid, key_db.replace('-', '_'))
    pix.save(os.path.join(OUTD, fn))
    tag = 'OK ' if mk == key_db else '!! '
    extra = ' [跨页]' if y1 >= pg.rect.y1 - 1 else ''
    p('%sid=%-5s db=%-10s 书=%-10s p%-4d y(%3d,%3d) hits=%d -> %s %dx%d%s' %
      (tag, tid, key_db, mk, best, y0, y1, len(score.get(best, [])), fn, pix.width, pix.height, extra))
    if mk != key_db:
        p('      候选页=%s 探针=%s' % (cand[:3], prs[:3]))
doc.close(); log.close()
print('done')
