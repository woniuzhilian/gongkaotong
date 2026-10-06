"""解析侧定位：在《公共基础分类版真题详解_答案解析》里按【年-号】切区，用解析文本探针命中并裁图"""
import os, re, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
OUTD = os.path.join(ROOT, '_a')
os.makedirs(OUTD, exist_ok=True)
log = open(os.path.join(ROOT, '_a_final.txt'), 'w', encoding='utf-8')
def p(*a): print(*a, file=log)

IDS = [8,40,60,61,131,136,143,243,254,256,278,371,375,376,380,382,383,486,496,501,552,613,615,623,625,721,731,735,737,779,812,855,856,863,971,987,993,1001,1011,1012,1014,1025,1028,1093,1095,1102,1103,1122,1140,1147,1149,1214,1217,1223,1329,1333,1336,1343,1344,1347,1372,1380,1381,1467,1524,1583,1645,1827,1828,1844]
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
PUB = [i for i in IDS if byid[i]['bigSubject'] == '公共基础']
PRO = [i for i in IDS if byid[i]['bigSubject'] != '公共基础']
p('公共基础 %d 题 / 专业基础 %d 题 (%s)' % (len(PUB), len(PRO), PRO))

CJK = re.compile(r'[一-鿿]{4,}')
def norm(s): return re.sub(r'\s+', '', s)
MARK = re.compile(r'【\s*(\d{4})\s*(补)?\s*[-–]\s*(\d+)\s*】')

def probes(q):
    out = []
    for f in ['analysis', 'question']:
        t = re.sub(r'\$[^$]*\$', ' ', str(q.get(f) or ''))
        t = re.sub(r'<br>|<img[^>]*>', ' ', t)
        for r in CJK.findall(t):
            if len(r) >= 5: out.append(norm(r)[:14])
    seen, keep = set(), []
    for x in sorted(out, key=len, reverse=True):
        if x not in seen: seen.add(x); keep.append(x)
    return keep[:10]

doc = pymupdf.open(os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf'))
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
p('答案书区间总数 %d  页数 %d' % (len(SEGS), doc.page_count))

def crop(tid, pno, y0, y1, suffix=''):
    pg = doc[pno]
    pix = pg.get_pixmap(clip=pymupdf.Rect(55, max(0, y0 - 3), pg.rect.x1 - 15, min(pg.rect.y1, y1 - 1)), dpi=200)
    fn = 'a%04d_%s%s.png' % (tid, key_of[tid].replace('-', '_'), suffix)
    pix.save(os.path.join(OUTD, fn))
    return fn, pix.width, pix.height

key_of = {}
nexact = nfix = nlow = 0
for tid in PUB:
    q = byid[tid]
    key_db = '%s-%s' % (q['year'], q['yearQnum'])
    key_of[tid] = key_db
    prs = probes(q)
    def score(seg): return sum(1 for x in prs if x and x in seg[4])
    cands = list(BYKEY.get(key_db, []))
    if prs:
        allhits = sorted([(score(s), s) for s in SEGS if score(s) > 0], key=lambda t: -t[0])
        for sc, s in allhits[:6]:
            if s not in cands: cands.append(s)
    if not cands:
        p('id=%-5s db=%-10s 未定位 hits=%s' % (tid, key_db, prs[:3])); nlow += 1; continue
    def yr(s): return s[1].split('-')[0]
    def nm(s):
        try: return int(s[1].split('-')[1])
        except Exception: return 999
    best = max(cands, key=lambda s: (score(s), 1 if s[1] == key_db else 0,
                                     1 if yr(s) == str(q['year']) else 0, -s[0]))
    top = score(best)
    tied = [c for c in cands if score(c) == top]
    if len(tied) > 1:
        tied.sort(key=lambda s: (0 if s[1] == key_db else 1,
                                 0 if yr(s) == str(q['year']) else 1,
                                 abs(nm(s) - nm(key_db))))
        best = tied[0]
    sc = score(best)
    key_of[tid] = best[1]
    tag = 'OK  ' if best[1] == key_db else ('FIX ' if sc >= 2 else 'LOW ')
    if best[1] == key_db: nexact += 1
    elif sc >= 2: nfix += 1
    else: nlow += 1
    fn, w, h = crop(tid, best[0], best[2], best[3])
    p('%sid=%-5s db=%-10s -> 书=%-10s p%-4d y(%3d,%3d) hits=%d/%d %s %dx%d' %
      (tag, tid, key_db, best[1], best[0], best[2], best[3], sc, len(prs), fn, w, h))
    if best[1] != key_db:
        p('       备选: %s' % ['%s p%d h=%d' % (c[1], c[0], score(c)) for c in cands[:4]])
    if best[3] >= doc[best[0]].rect.y1 - 1:
        npg = doc[best[0] + 1]
        nb = [b for b in npg.get_text('blocks') if MARK.search(b[4])]
        ny = min([b[1] for b in nb], default=npg.rect.y1)
        pix = npg.get_pixmap(clip=pymupdf.Rect(55, 0, npg.rect.x1 - 15, max(80, ny - 3)), dpi=200)
        f2 = 'a%04d_%s_b.png' % (tid, best[1].replace('-', '_'))
        pix.save(os.path.join(OUTD, f2))
        p('       续页 -> %s %dx%d' % (f2, pix.width, pix.height))
doc.close(); log.close()
print('exact=%d fixed=%d low=%d' % (nexact, nfix, nlow))
