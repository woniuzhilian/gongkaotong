# -*- coding: utf-8 -*-
"""T5 判据实验：只用题库文本，看 : ; 的粘连上下文能否可靠判定它是 +/−"""
import io, os, re, json, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
data = json.load(io.open(os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json'), encoding='utf-8'))
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']
B = chr(92)
CMDRE = re.compile(B + B + '[A-Za-z]+')
OUT = io.open(os.path.join(ROOT, '_t5_glue.txt'), 'w', encoding='utf-8')


def spans(t):
    r, s = [], -1
    for i, c in enumerate(t):
        if c != '$':
            continue
        if s < 0:
            s = i
        else:
            r.append((s, i)); s = -1
    return r


def cls(c):
    if c == '':
        return 'E'
    if c.isascii() and c.isalnum():
        return 'A'
    if c in '})]':
        return 'C'
    if c in '({[':
        return 'O'
    if c.isspace():
        return 'S'
    if c == B:
        return 'B'
    if ord(c) > 0x2000:
        return 'M'
    return 'P'


bk = collections.Counter()
samp = collections.defaultdict(list)
tidu = collections.defaultdict(set)
for q in data:
    for f in FIELDS:
        t = str(q.get(f) or '')
        if ':' not in t and ';' not in t:
            continue
        for a, b in spans(t):
            seg = t[a + 1:b]
            for i, c in enumerate(seg):
                if c not in ':;':
                    continue
                g = t[a + 1 + i - 1] if i > 0 else ''
                h = t[a + 1 + i + 1] if a + 1 + i + 1 < b else ''
                s = '%s %s>%s %s' % (c, cls(g), cls(h), 'glue' if cls(g) in 'ACMO' and cls(h) in 'ACO' else '')
                bk[s.strip()] += 1
                tidu[s.strip()] |= {q['id']}
                if len(samp[s.strip()]) < 9:
                    samp[s.strip()].append('id=%d %s …%s…' % (q['id'], f, t[max(0, a + 1 + i - 16):a + 1 + i + 17]))
for s, n in bk.most_common():
    OUT.write('\n### %-14s %3d 处  %3d 题\n' % (s, n, len(tidu[s])))
    for x in samp[s]:
        OUT.write('    %s\n' % x)
OUT.write('\n总=%d\n' % sum(bk.values()))
OUT.close()
print('sites=%d kinds=%d' % (sum(bk.values()), len(bk)))
