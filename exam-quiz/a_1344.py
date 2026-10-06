import os, re, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
q = byid[1344]
def norm(s): return re.sub(r'\s+', '', s)
MARK = re.compile(r'【\s*(\d{4})\s*(补)?\s*[-–]\s*(\d+)\s*】')
doc = pymupdf.open(os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf'))
out = ['库 db=%s-%s 答案=%s' % (q['year'], q['yearQnum'], q['answer']),
       '库解析: %s' % norm(str(q.get('analysis')))]
KEYS = ['2024-%d' % n for n in range(20, 36)]
for pno in range(doc.page_count):
    pg = doc[pno]
    blocks = [b for b in pg.get_text('blocks') if b[4].strip()]
    ms = []
    for b in blocks:
        m = MARK.search(b[4])
        if m: ms.append((b[1], m.group(1) + '-' + str(int(m.group(3)))))
    ms.sort()
    for i, (y, k) in enumerate(ms):
        if k not in KEYS: continue
        y1 = ms[i + 1][0] if i + 1 < len(ms) else pg.rect.y1
        txt = norm(''.join(b[4] for b in blocks if y - 1 <= b[1] < y1 - 1))
        out.append('%-9s p%-3d y(%3d,%3d) %s' % (k, pno, y, y1, txt[:110]))
open('_a_1344.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
