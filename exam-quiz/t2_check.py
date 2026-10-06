# -*- coding: utf-8 -*-
"""T2 应用后核对：只允许 _t2_new.json 记录的 (id,field) 变化，其余逐字段一致"""
import os, io, json

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
NEW = os.path.join(ROOT, '_t2_new.json')
CUR = json.load(open(DB, encoding='utf-8'))
OLD = json.load(open(os.path.join(ROOT, '_fix_backup', 'questions_BEFORE_T2.json'), encoding='utf-8'))
EXP = json.load(open(NEW, encoding='utf-8'))

out = []
assert len(CUR) == len(OLD), '题数不同'
nid = sum(1 for a, b in zip(CUR, OLD) if a['id'] != b['id'])
out.append('id序列不一致数=%d' % nid)

nd, extra, missing = 0, [], []
for q in CUR:
    o = next(x for x in OLD if x['id'] == q['id'])
    if set(q.keys()) != set(o.keys()):
        out.append('键集变化 id=%s' % q['id'])
    for k in q:
        if q[k] == o[k]:
            continue
        nd += 1
        want = EXP.get(str(q['id']), {}).get(k)
        if want is None:
            extra.append('%s/%s' % (q['id'], k))
        elif want != q[k]:
            extra.append('%s/%s 值与提案不符' % (q['id'], k))
for s, d in EXP.items():
    for k in d:
        if CUR[[x['id'] for x in CUR].index(int(s))][k] != d[k]:
            missing.append('%s/%s' % (s, k))

out.append('实际变化字段数=%d  提案=%d' % (nd, sum(len(v) for v in EXP.values())))
out.append('提案外变化=%d %s' % (len(extra), extra[:5]))
out.append('提案未生效=%d %s' % (len(missing), missing[:5]))

toks = ['\\varsigma', '\\epsilon', '\\Theta', '\\cdots^{1}', ',\\sigma-']
res = []
for q in CUR:
    for k, v in q.items():
        if isinstance(v, str):
            for t in toks:
                if t in v:
                    res.append('%s/%s %s' % (q['id'], k, t))
out.append('T3 错映射残留=%d %s' % (len(res), res[:8]))

bad = []
for q in CUR:
    for k in ('question', 'A', 'B', 'C', 'D', 'analysis'):
        v = q.get(k) or ''
        if v.count('$') % 2 or '$$' in v:
            bad.append('%s/%s' % (q['id'], k))
out.append('全库奇数$/相邻$$=%d %s' % (len(bad), bad[:8]))

with io.open(os.path.join(ROOT, '_t2_check.txt'), 'w', encoding='utf-8', newline='\r\n') as fh:
    fh.write('\n'.join(out))
print('ok')
