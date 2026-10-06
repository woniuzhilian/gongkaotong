# -*- coding: utf-8 -*-
"""T3 扩展清点：数学片段内出现 : ; , ] 等可疑错映射字符的上下文"""
import os, re, json, io

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
data = json.load(open(DB, encoding='utf-8'))
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']
BS2 = chr(92) * 2

out = io.open(os.path.join(ROOT, '_t3_punct.txt'), 'w', encoding='utf-8')
buckets = {}
for q in data:
    for f in FIELDS:
        t = str(q.get(f) or '')
        for m in re.finditer('[$]([^$]+)[$]', t):
            frag = m.group(1)
            for mm in re.finditer('[;:]', frag):
                a, b2 = max(0, mm.start() - 16), min(len(frag), mm.end() + 16)
                buckets.setdefault(mm.group(0), []).append((q['id'], f, frag[a:b2]))
for k in [';', ':']:
    v = buckets.get(k, [])
    ids = sorted(set(i for i, _, _ in v))
    out.write('===== 片段内 %r  命中 %d 处 / %d 题\n' % (k, len(v), len(ids)))
    seen = set()
    for i, f, ctx in v:
        key = ctx[:12]
        if key in seen:
            continue
        seen.add(key)
        out.write('   id=%-5s %-9s %s\n' % (i, f, ctx))
    out.write('   ids=%s\n\n' % ids)
out.close()
print('semicolon=%d colon=%d' % (len(buckets.get(';', [])), len(buckets.get(':', []))))
