import os, re, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
out = []
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
def norm(s): return re.sub(r'\s+', '', s)
def cjk(s): return re.sub(r'[^一-鿿]', '', s)
MARK = re.compile(r'【\s*(\d{4})\s*(补)?\s*[-–]\s*(\d+)\s*】')
ANS = re.compile(r'】\s*答案[:：]\s*([A-D])')
KAO = re.compile(r'【考点分析】(.*?)【解析】', re.S)

doc = pymupdf.open(os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf'))
REG = {}
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
        REG.setdefault((k, pno), []).append((y, y1, txt, a.group(1) if a else '?'))

sel = {}
for ln in open(os.path.join(ROOT, '_a_final.txt'), encoding='utf-8'):
    m = re.search(r'id=(\d+)\s+db=(\S+)\s+-> 书=(\S+)\s+p(\d+)', ln)
    if m: sel[int(m.group(1))] = (m.group(3), int(m.group(4)))

bad = []
for tid, (key, pno) in sorted(sel.items()):
    q = byid[tid]
    r = [x for x in REG.get((key, pno), [])]
    if not r:
        bad.append((tid, 'no-region')); continue
    y0, y1, txt, ansl = r[0]
    kao = KAO.search(txt)
    book_kao = cjk(kao.group(1)) if kao else ''
    db_head = cjk(re.split(r'[.。]', str(q.get('analysis') or ''))[0])[:20]
    # 考点分析 与 库解析首句 的互相包含度
    if not book_kao or not db_head:
        ov = 0.0
    else:
        s1 = set(book_kao); s2 = set(db_head)
        ov = len(s1 & s2) / max(1, len(s2))
    ok = (ov >= 0.7) and ansl == str(q.get('answer'))
    if not ok:
        bad.append((tid, 'ov=%.2f 书答案=%s 库答案=%s 书考点=%s 库首=%s' % (ov, ansl, q.get('answer'), book_kao[:16], db_head[:16])))
out.append('不合格 %d / %d' % (len(bad), len(sel)))
for t, why in bad: out.append('id=%-5s %s' % (t, why))

for f in ['岩土专业基础分类真题解析（16~24）_答案解析.pdf', '岩土专业基础分类真题解析（16~24）_题目.pdf',
          '公共基础分类版真题详解（13~24）_答案解析.pdf']:
    d = pymupdf.open(os.path.join(P, f))
    toc = d.get_toc()
    out.append('--- %s toc=%d' % (f, len(toc)))
    for t in toc[:25]: out.append('    %s p%s' % (t[1][:40], t[2]))
open('_a_check2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('bad=%d' % len(bad))
