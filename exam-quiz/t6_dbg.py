# -*- coding: utf-8 -*-
import json
import re
import t6_fix as T

d = json.load(open('exam-quiz/src/data/questions.json', encoding='utf-8'))
by = {q['id']: q for q in d}
out = []
for tid, f in ((13, 'question'), (32, 'A'), (52, 'question')):
    v = by[tid][f]
    nv, nt = T.fix_field(v)
    a = re.sub(r'\$', '', nv)
    b = re.sub(r'\$', '', v)
    out.append('== id=%d %s' % (tid, f))
    out.append('  ORIG %r' % v)
    out.append('  NEW  %r' % nv)
    out.append('  notes %s' % nt)
    out.append('  stripA %r' % b[:200])
    out.append('  stripB %r' % a[:200])
    for i, (x, y) in enumerate(zip(b, a)):
        if x != y:
            out.append('  first char diff @%d %r vs %r' % (i, b[max(0,i-30):i+30], a[max(0,i-30):i+30]))
            break
open('_t6_dbg.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done')
