# -*- coding: utf-8 -*-
"""#5 普查：$...$ 片段内部的 : 和 ; 出现位置与上下文签名"""
import os, re, io, json, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']
data = json.load(io.open(DB, encoding='utf-8'))


def kcat(c):
    if c == '':
        return '#'
    if c.isdigit():
        return 'D'
    if 'a' <= c <= 'z' or 'A' <= c <= 'Z':
        return 'L'
    if c == chr(92):
        return 'B'
    if c in '{([':
        return 'K'
    if c in '})]':
        return 'R'
    if c in '=-+*/<>|,':
        return 'P'
    if c.isspace():
        return 'S'
    if '一' <= c <= '鿿':
        return 'C'
    return 'o'


sig = collections.Counter()
ex = collections.defaultdict(list)
rows = []
lab = 0
for q in data:
    tid = q['id']
    for f in FIELDS:
        t = q.get(f) or ''
        if not t:
            continue
        for fm in re.finditer(r'\$([^$]+)\$', t):
            inner = fm.group(1)
            for i, c in enumerate(inner):
                if c not in ':;':
                    continue
                prev = inner[max(0, i - 14):i]
                nxt = inner[i + 1:i + 15]
                s = '%s|%s>%s' % (c, kcat(prev[-1] if prev else ''), kcat(nxt[0] if nxt else ''))
                sig[s] += 1
                if len(ex[s]) < 6:
                    ex[s].append('id=%d %s  …%s[%s]%s…' % (tid, f, prev, c, nxt))
                lab += 1
                rows.append('%d\t%s\t%s\t%s\t%s' % (tid, f, c, prev + '\u241f' + nxt, s))

out = []
out.append('总命中=%d 处（含 : 与 ;），候选点编号已写入 _t5_census.tsv' % lab)
out.append('')
for s, n in sig.most_common():
    out.append('### %-8s %4d 处' % (s, n))
    for e in ex[s]:
        out.append('    ' + e)
    out.append('')
io.open(os.path.join(ROOT, '_t5_census.txt'), 'w', encoding='utf-8', newline='\r\n').write('\n'.join(out))
with io.open(os.path.join(ROOT, '_t5_census.tsv'), 'w', encoding='utf-8', newline='\r\n') as fh:
    fh.write('id\tfield\tch\tctx\t\n'.replace('\t', '\t'))
    for r in rows:
        fh.write(r + '\n')
qs = len(set(int(r.split('\t')[0]) for r in rows))
print('sites=%d questions=%d' % (lab, qs))
