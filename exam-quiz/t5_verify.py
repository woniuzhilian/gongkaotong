# -*- coding: utf-8 -*-
"""Verify the T5 apply touched nothing but sign characters."""
import json

a = json.load(open('_fix_backup/questions_BEFORE_T5.json', encoding='utf-8'))
b = json.load(open('exam-quiz/src/data/questions.json', encoding='utf-8'))
FIELDS = ('question', 'A', 'B', 'C', 'D', 'analysis')
assert len(a) == len(b), 'length drift'
nq = nf = nflip = 0
bad = []
for qa, qb in zip(a, b):
    assert qa['id'] == qb['id']
    for k in set(qa) | set(qb):
        if k in FIELDS:
            continue
        if qa.get(k) != qb.get(k):
            bad.append('non-text key %s changed in id=%s' % (k, qa['id']))
    for f in FIELDS:
        va, vb = qa.get(f) or '', qb.get(f) or ''
        if va == vb:
            continue
        nf += 1
        nq += 1
        if len(va) != len(vb):
            bad.append('length changed id=%s %s' % (qa['id'], f))
            continue
        for i, (ca, cb) in enumerate(zip(va, vb)):
            if ca == cb:
                continue
            if (ca, cb) in ((':', '+'), (';', '-')):
                nflip += 1
            else:
                bad.append('id=%s %s @%d %r->%r' % (qa['id'], f, i, ca, cb))
print('fields_changed=%d questions=%d sign_flips=%d unexpected=%d' % (nf, len(set(
    q['id'] for q, r in zip(a, b) if any((q.get(f) or '') != (r.get(f) or '') for f in FIELDS))), nflip, len(bad)))
for x in bad[:20]:
    print('  !!', x)
