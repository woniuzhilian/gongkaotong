"""逐题定位：把探针归属到具体的【年-号】区间，取命中最多的区间；跨页时补裁续页"""
import os, re, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
OUTD = os.path.join(ROOT, '_t1')
log = open(os.path.join(ROOT, '_t1_final.txt'), 'w', encoding='utf-8')
def p(*a): print(*a, file=log)

IDS = [8,12,17,61,131,136,167,207,253,256,267,318,326,371,376,380,
       383,413,492,501,521,615,617,623,684,731,735,737,855,856,863,
       971,973,976,1020,1095,1103,1122,1140,1214,1217,1280,1294,1336,
       1372,1375,1380,1410]
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}

CJK = re.compile(r'[一-鿿]{4,}')
def norm(s): return re.sub(r'\s+', '', s)
MARK = re.compile(r'【\s*(\d{4})\s*(补)?\s*[-–]\s*(\d+)\s*】')

def probes(q):
    out = []
    for f in ['question', 'A', 'B', 'C', 'D']:
        t = re.sub(r'\$[^$]*\$', ' ', str(q.get(f) or ''))
        t = re.sub(r'<br>|<img[^>]*>', ' ', t)
        for r in CJK.findall(t):
            if len(r) >= 5: out.append(norm(r)[:16])
    seen, keep = set(), []
    for x in sorted(out, key=len, reverse=True):
        if x not in seen: seen.add(x); keep.append(x)
    return keep[:8]

doc = pymupdf.open(os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf'))
# 每页拆成若干【年-号】区间，预存区间文本
SEGS = []   # (pno, key, y0, y1, text)
for pno in range(doc.page_count):
    pg = doc[pno]
    blocks = [b for b in pg.get_text('blocks') if b[4].strip()]
    ms = []
    for b in blocks:
        m = MARK.search(b[4])
        if m: ms.append((b[1], m.group(1) + ('补' if m.group(2) else '') + '-' + str(int(m.group(3)))))
    ms.sort()
    for i, (y, k) in enumerate(ms):
        y1 = ms[i + 1][0] if i + 1 < len(ms) else pg.rect.y1
        txt = norm(''.join(b[4] for b in blocks if y - 1 <= b[1] < y1 - 1))
        SEGS.append((pno, k, y, y1, txt))
BYKEY = {}
for s in SEGS: BYKEY.setdefault(s[1], []).append(s)
p('区间总数 %d' % len(SEGS))
def preview(t): return re.sub(r'\s+','',t)[:46]

def crop(tid, seg, suffix=''):
    pno, key, y0, y1, _ = seg
    pg = doc[pno]
    pix = pg.get_pixmap(clip=pymupdf.Rect(60, max(0, y0 - 3), pg.rect.x1 - 20, min(pg.rect.y1, y1 - 3)), dpi=200)
    fn = 'f%04d_%s%s.png' % (tid, key.replace('-', '_'), suffix)
    pix.save(os.path.join(OUTD, fn))
    return fn, pix.width, pix.height

nexact = nfix = nfallback = 0
for tid in IDS:
    q = byid[tid]
    key_db = '%s-%s' % (q['year'], q['yearQnum'])
    prs = probes(q)
    def score(seg):
        return sum(1 for x in prs if x and x in seg[4])
    cands = list(BYKEY.get(key_db, []))
    if prs:
        allhits = [(score(s), s) for s in SEGS if score(s) > 0]
        allhits.sort(key=lambda t: -t[0])
        for sc, s in allhits[:6]:
            if s not in cands: cands.append(s)
    if not cands:
        p('id=%-5s db=%-10s 未定位' % (tid, key_db)); nfallback += 1; continue
    best = max(cands, key=lambda s: (score(s), 1 if s[1] == key_db else 0, -s[0]))
    sc = score(best)
    tag = 'OK  ' if best[1] == key_db else ('FIX ' if sc >= 2 else 'LOW ')
    if best[1] == key_db: nexact += 1
    elif sc >= 2: nfix += 1
    else: nfallback += 1
    fn, w, h = crop(tid, best)
    p('%sid=%-5s db=%-10s -> 书=%-10s p%-4d y(%3d,%3d) hits=%d/%d %s %dx%d' %
      (tag, tid, key_db, best[1], best[0], best[2], best[3], sc, len(prs), fn, w, h))
    if best[1] != key_db:
        p('       备选: %s' % ['%s p%d h=%d' % (c[1], c[0], score(c)) for c in cands[:4]])
    if best[3] >= doc[best[0]].rect.y1 - 1:
        npg = doc[best[0] + 1]
        nb = [b for b in npg.get_text('blocks') if MARK.search(b[4])]
        ny = min([b[1] for b in nb], default=npg.rect.y1)
        pix = npg.get_pixmap(clip=pymupdf.Rect(60, 0, npg.rect.x1 - 20, max(60, ny - 3)), dpi=200)
        f2 = 'f%04d_%s_b.png' % (tid, best[1].replace('-', '_'))
        pix.save(os.path.join(OUTD, f2))
        p('       续页 -> %s %dx%d' % (f2, pix.width, pix.height))
doc.close(); log.close()
print('exact=%d fixed=%d low=%d' % (nexact, nfix, nfallback))
