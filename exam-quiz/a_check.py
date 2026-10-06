import os, re, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
out = []
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}

def norm(s): return re.sub(r'\s+', '', s)
MARK = re.compile(r'【\s*(\d{4})\s*(补)?\s*[-–]\s*(\d+)\s*】')
ANS = re.compile(r'】\s*答案[:：]\s*([A-D])')

doc = pymupdf.open(os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf'))
SEGS = []
for pno in range(doc.page_count):
    pg = doc[pno]
    blocks = [b for b in pg.get_text('blocks') if b[4].strip()]
    ms = []
    for b in blocks:
        m = MARK.search(b[4])
        if m: ms.append((b[1], m.group(1) + ('补' if m.group(2) else '') + '-' + str(int(m.group(3))), b[4]))
    ms.sort()
    for i, (y, k, raw) in enumerate(ms):
        y1 = ms[i + 1][0] if i + 1 < len(ms) else pg.rect.y1
        txt = norm(''.join(b[4] for b in blocks if y - 1 <= b[1] < y1 - 1))
        a = ANS.search(raw)
        SEGS.append((pno, k, y, y1, txt, a.group(1) if a else '?'))
BYKEY = {}
for s in SEGS: BYKEY.setdefault(s[1], []).append(s)

# 从 _a_final.txt 读回每题选定的书键
sel = {}
for ln in open(os.path.join(ROOT, '_a_final.txt'), encoding='utf-8'):
    m = re.search(r'id=(\d+)\s+db=(\S+)\s+-> 书=(\S+)\s+p(\d+)', ln)
    if m: sel[int(m.group(1))] = (m.group(3), int(m.group(4)))
out.append('已定位 %d 题' % len(sel))

def bigrams(s):
    return set(s[i:i + 2] for i in range(len(s) - 1))

flag = 0
for tid, (key, pno) in sorted(sel.items()):
    q = byid[tid]
    cands = [s for s in BYKEY.get(key, []) if s[0] == pno]
    if not cands:
        out.append('!! id=%-5s 找不到区间 %s p%d' % (tid, key, pno)); flag += 1; continue
    seg = cands[0]
    book = seg[4]
    ana = norm(re.sub(r'<br>|<img[^>]*>', '', str(q.get('analysis') or '')))
    stem = norm(re.sub(r'\$[^$]*\$|<br>|<img[^>]*>', '', str(q.get('question') or '')))
    b2, a2 = bigrams(book), bigrams(ana)
    cover = len(b2 & a2) / max(1, len(b2))
    stemhit = sum(1 for r in re.findall(r'[一-鿿]{4,}', stem) if norm(r) in book)
    ansok = seg[5] == str(q.get('answer'))
    if cover < 0.35 or stemhit == 0 or not ansok:
        flag += 1
        out.append('?? id=%-5s 书=%-10s p%-3d 答案书=%s 库=%s 二元覆盖=%.2f 题干命中=%d' %
                   (tid, key, pno, seg[5], q.get('answer'), cover, stemhit))
        out.append('      书首: %s' % book[:70])
        out.append('      库首: %s' % ana[:70])
out.append('可疑 %d 题' % flag)

# 专业基础答案解析是否有文字层
d2 = pymupdf.open(os.path.join(P, '岩土专业基础分类真题解析（16~24）_答案解析.pdf'))
tc = sum(len(d2[i].get_text()) for i in range(d2.page_count))
imgs = sum(len(d2[i].get_images()) for i in range(d2.page_count))
out.append('pro答案 pages=%d 总字符=%d 图片数=%d' % (d2.page_count, tc, imgs))
d3 = pymupdf.open(os.path.join(P, '岩土专业基础分类真题解析（16~24）_题目.pdf'))
tc3 = sum(len(d3[i].get_text()) for i in range(d3.page_count))
out.append('pro题目 pages=%d 总字符=%d' % (d3.page_count, tc3))
for i in [1467, 1524, 1583, 1645, 1827, 1828, 1844]:
    q = byid[i]
    out.append('id=%-5s %s/%s yearQnum=%s 答案=%s 解析前=%s' %
               (i, q['bigSubject'], q['smallSubject'], q['yearQnum'], q['answer'],
                norm(str(q.get('analysis') or ''))[:40]))
open('_a_check.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('flag=%d' % flag)
