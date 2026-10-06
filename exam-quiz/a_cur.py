import os, re, json
ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
sel = {}
for ln in open(os.path.join(ROOT, '_a_final.txt'), encoding='utf-8'):
    m = re.search(r'id=(\d+)\s+db=(\S+)\s+-> 书=(\S+)\s+p(\d+)', ln)
    if m: sel[int(m.group(1))] = m.group(3)
sel[1344] = '2024-25'
out = []
nimg = 0
for tid in sorted(sel):
    q = byid[tid]
    a = str(q.get('analysis') or '')
    imgs = re.findall(r'<img[^>]*>', a)
    if imgs:
        nimg += 1
        out.append('id=%-5s 书=%-10s 含%d图: %s' % (tid, sel[tid], len(imgs), ' '.join(imgs)))
    out.append('id=%-5s len=%d :: %s' % (tid, len(a), a.replace('\n', ' ')[:520]))
out.insert(0, '含图的解析题数=%d / %d' % (nimg, len(sel)))
open('_a_cur.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok %d' % len(sel))
