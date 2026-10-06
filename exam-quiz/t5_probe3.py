# -*- coding: utf-8 -*-
import json
import io

d = json.load(open('exam-quiz/src/data/questions.json', encoding='utf-8'))
by = {q['id']: q for q in d}
out = []
for tid in (1082, 108, 400, 733, 11):
    q = by[tid]
    for f in ('question', 'A', 'B', 'C', 'D', 'analysis'):
        v = q.get(f) or ''
        out.append('== %d %s dollars=%d' % (tid, f, v.count('$')))
        out.append('   ' + v[:700])
io.open('_t5_probe3.txt', 'w', encoding='utf-8', newline='\r\n').write('\n'.join(out))
print('ok')
