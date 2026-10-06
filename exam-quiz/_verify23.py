"""收尾校验：23 道重选题的选项是否完整、引用图片是否都存在、JSON 是否合法"""
import os, re, json

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
IMGROOT = os.path.join(ROOT, 'exam-quiz', 'public')
IDS = [306, 448, 546, 568, 658, 666, 669, 693, 784, 813, 904, 908, 928, 932,
       1040, 1050, 1053, 1147, 1160, 1262, 1292, 1588, 2002]

data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
log = open(os.path.join(ROOT, '_verify23.txt'), 'w', encoding='utf-8')


def p(*a):
    print(*a, file=log)


existing = set()
for dirpath, _dn, fns in os.walk(IMGROOT):
    for fn in fns:
        rel = os.path.relpath(os.path.join(dirpath, fn), IMGROOT)
        existing.add('/' + rel.replace(os.sep, '/'))

p('题库总数: %d' % len(data))
bad = 0
newimg = 0
for tid in IDS:
    q = byid.get(tid)
    if q is None:
        p('!! id=%s 不存在' % tid)
        bad += 1
        continue
    problems = []
    for L in 'ABCD':
        v = (q.get(L) or '').strip()
        if not v:
            problems.append('选项%s为空' % L)
    refs = re.findall(r'src="([^"]+)"', q.get('question', '') + ''.join(
        q.get(L) or '' for L in 'ABCD'))
    for r in refs:
        if r not in existing:
            problems.append('图片缺失 %s' % r)
        if r.startswith('/images/q23/'):
            newimg += 1
    if not refs and re.search(r'如图|图示|下图|图中', q.get('question') or ''):
        problems.append('题干含"如图/图示"但无配图')
    flag = 'OK ' if not problems else 'BAD'
    p('%s id=%-5s %-8s %s-%-3s 答%s  图数=%s  %s' % (
        flag, tid, q['bigSubject'], q['year'], q['yearQnum'], q['answer'],
        len(refs), '; '.join(problems)))
    if problems:
        bad += 1
p('\n结果: %d/%d 通过, %d 项仍有问题' % (len(IDS) - bad, len(IDS), bad))
p('q23 目录文件数: %d' % len(os.listdir(os.path.join(IMGROOT, 'images', 'q23'))))
log.close()
print('bad=%d' % bad)
