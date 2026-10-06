# -*- coding: utf-8 -*-
"""T5 复核清单：题库内数学片段中所有 : ; 站点，带上下文与原书同键判定"""
import io, os, re, sys, json, types, collections, unicodedata, pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(ROOT, 't5_prop.py'), encoding='utf-8').read()
head = src.split('doc = pymupdf.open(BK)')[0].replace(
    "OUT = io.open(os.path.join(ROOT, '_t5_prop.txt'), 'w', encoding='utf-8')",
    "OUT = io.open(os.devnull, 'w', encoding='utf-8')")
ns = {'os': os, 're': re, 'io': io, 'json': json, 'sys': sys, 'ROOT': ROOT, '__file__': os.path.join(ROOT, 't5_prop.py'),
      'collections': collections, 'unicodedata': unicodedata, 'pymupdf': pymupdf}
exec(compile(head, 't5_prop.py', 'exec'), ns)
T = types.SimpleNamespace(**ns)
doc, docq = pymupdf.open(T.BK), pymupdf.open(T.BKQ)
SP = set(' \t\n\r' + chr(160) + chr(12288) + chr(8194) + chr(8195) + chr(8201) + chr(8202))
CONF = json.load(io.open(os.path.join(ROOT, '_t5_edits.json'), encoding='utf-8'))
CONFI = {(int(k), f, e[0]) for k, v in CONF.items() for f, lst in v.items() for e in lst}
OPERAND = set(')]}')


def ish(ch):
    return bool(T.norm(ch)) or ch in OPERAND or (ch and ord(ch) > 0x2000)


def osh(ch):
    return bool(T.norm(ch)) or ch in '([{' or (ch and ord(ch) > 0x2000)


rows = []
for q in T.data:
    tid = q['id']
    qpr = T.probes_of(str(q.get('question') or ''))
    apr = T.probes_of(str(q.get('analysis') or ''))
    cpr = sorted(set(qpr) | set(apr), key=len, reverse=True)[:6]
    ea = T.entry_rect(doc, 'A', '', cpr) or T.entry_rect(doc, 'A', '', apr) or T.entry_rect(doc, 'A', '', qpr)
    eq = T.entry_rect(docq, 'Q', '', cpr) or T.entry_rect(docq, 'Q', '', qpr)
    bs = []
    for d, tag, e in ((doc, 'A', ea), (docq, 'Q', eq)):
        if e:
            bs += T.book_sites(T.entry_lines(d, tag, e[0], e[1]))
    bk = collections.defaultdict(set)
    for s in bs:
        if not s['script'] and s['nb'] >= 1 and s['na'] >= 1:
            bk[s['key']].add(s['ch'] + '>' + s['new'])
    for f in T.FIELDS:
        t = str(q.get(f) or '')
        if ':' not in t and ';' not in t:
            continue
        atoms, pos = T.db_stream(t)
        for a, b in T.math_spans(t):
            for i in range(a + 1, b):
                c = t[i]
                if c not in ':;':
                    continue
                g = t[i - 1] if i - 1 > a else ''
                h = t[i + 1] if i + 1 < b else ''
                glue = 'G' if (ish(g) and osh(h)) else '-'
                k, nb, na = T.key_of(atoms, pos, i)
                ev = bk.get(k)
                mark = '★' if (tid, f, i) in CONFI else ('书' + '/'.join(sorted(ev)) if ev else '')
                rows.append((tid, f, i, c, glue, mark,
                             t[max(0, i - 26):i] + '«' + c + '»' + t[i + 1:i + 27]))
OUT = io.open(os.path.join(ROOT, '_t5_review.txt'), 'w', encoding='utf-8')
OUT.write('数学片段内 : ; 站点 %d 处；G=两侧粘连 书=原书同键判定 ★=已提案\n' % len(rows))
OUT.write('图例: 题号 字段 位置 字符 粘连 书证  上下文\n\n')
cur = None
for r in sorted(rows, key=lambda z: (z[4] != 'G', z[0], z[1], z[2])):
    if r[0] != cur:
        OUT.write('\n')
        cur = r[0]
    OUT.write('%-5d %-8s %4d %s %s %-10s …%s…\n' % r)
OUT.close()
doc.close()
docq.close()
print('sites=%d glue=%d' % (len(rows), sum(1 for r in rows if r[4] == 'G')))
