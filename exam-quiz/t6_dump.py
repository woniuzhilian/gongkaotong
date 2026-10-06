# -*- coding: utf-8 -*-
import json
import io
import sys

d = json.load(open('exam-quiz/src/data/questions.json', encoding='utf-8'))
by = {q['id']: q for q in d}
out = []
for tid in [int(x) for x in sys.argv[1:]]:
    q = by[tid]
    for f in ('question', 'A', 'B', 'C', 'D', 'analysis'):
        v = q.get(f) or ''
        if '$' not in v:
            continue
        out.append('== id=%d %s dollars=%d' % (tid, f, v.count('$')))
        out.append('   ' + v)
io.open('_t6_dump.txt', 'w', encoding='utf-8', newline='\r\n').write('\n'.join(out))
print('ok', len(out) // 2)
