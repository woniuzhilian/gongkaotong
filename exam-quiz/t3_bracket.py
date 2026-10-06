# -*- coding: utf-8 -*-
"""T3 扩展清点：方括号错映射 ,cmd- -> [cmd] 的规模"""
import os, re, json, io

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
data = json.load(open(DB, encoding='utf-8'))
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']
B = chr(92)

out = io.open(os.path.join(ROOT, '_t3_bracket.txt'), 'w', encoding='utf-8')
hits = {}
for q in data:
    for f in FIELDS:
        t = str(q.get(f) or '')
        if not t:
            continue
        for m in re.finditer(',' + chr(92) * 2 + '([a-zA-Z]+)-', t):
            a, b2 = max(0, m.start() - 20), min(len(t), m.end() + 20)
            hits.setdefault(m.group(1), []).append((q['id'], f, t[a:b2].replace('\n', ' ')))
tot = 0
for k, v in sorted(hits.items(), key=lambda x: -len(x[1])):
    ids = sorted(set(i for i, _, _ in v))
    tot += len(ids)
    out.write('===== ,\\%s-  命中 %d 处 / %d 题\n' % (k, len(v), len(ids)))
    for i, f, ctx in v[:6]:
        out.write('   id=%-5s %-9s ...%s...\n' % (i, f, ctx))
allq = sorted(set(i for v in hits.values() for i, _, _ in v))
out.write('\n涉及题数(去重)=%d\n%s\n' % (len(allq), allq))
out.close()
print('occ=%d q=%d keys=%s' % (sum(len(v) for v in hits.values()), len(allq), sorted(hits)))
