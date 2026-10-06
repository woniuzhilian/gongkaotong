# -*- coding: utf-8 -*-
"""T5 定位体检：打印每题在答案解析册里定位到的条目原文，人工判断定位是否正确"""
import io, os, re, sys, json, types, collections, unicodedata, pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(ROOT, 't5_prop.py'), encoding='utf-8').read()
head = src.split('doc = pymupdf.open(BK)')[0]
head = head.replace("OUT = io.open(os.path.join(ROOT, '_t5_prop.txt'), 'w', encoding='utf-8')",
                    "OUT = io.open(os.devnull, 'w', encoding='utf-8')")
ns = {'os': os, 're': re, 'io': io, 'json': json, 'sys': sys, 'ROOT': ROOT, '__file__': os.path.join(ROOT, 't5_prop.py'),
      'collections': collections, 'unicodedata': unicodedata, 'pymupdf': pymupdf}
exec(compile(head, 't5_prop.py', 'exec'), ns)
T = types.SimpleNamespace(**ns)
T.doc = pymupdf.open(T.BK)
T.docq = pymupdf.open(T.BKQ)

OUT = io.open(os.path.join(ROOT, '_t5_loc.txt'), 'w', encoding='utf-8')
byid = {q['id']: q for q in T.data}
for tid in [int(x) for x in sys.argv[1:]]:
    q = byid[tid]
    qpr = T.probes_of(str(q.get('question') or ''))
    apr = T.probes_of(str(q.get('analysis') or ''))
    cpr = sorted(set(qpr) | set(apr), key=len, reverse=True)[:6]
    ea = (T.entry_rect(T.doc, 'A', '', cpr) or T.entry_rect(T.doc, 'A', '', apr)
          or T.entry_rect(T.doc, 'A', '', qpr))
    OUT.write('\n===== id=%d\n  qpr=%s\n  apr=%s\n' % (tid, qpr[:3], apr[:3]))
    OUT.write('  DB Q : %s\n  DB A : %s\n' % (str(q.get('question'))[:150], str(q.get('analysis'))[:200]))
    if not ea:
        OUT.write('  答案解析未定位\n')
        continue
    OUT.write('  条目 p%d rect=%s hit=%d\n' % (ea[0], [round(v) for v in ea[1]], ea[2]))
    ls = T.entry_lines(T.doc, 'A', ea[0], ea[1])
    for ln in ls:
        OUT.write('   | %s\n' % ''.join(x['t'] for x in ln)[:200])
    bs = T.book_sites(ls)
    OUT.write('  -- 符号点 %d / 可用键 %d\n' % (len(bs), len(set(
        s['key'] for s in bs if not s['script'] and s['nb'] >= T.MINCTX and s['na'] >= T.MINCTX))))
    for s in bs:
        OUT.write('     BOOK k=%-18s %s->%s scr=%d nb=%d na=%d …%s…\n' % (
            s['key'], s['ch'], s['new'], s['script'], s['nb'], s['na'], s['raw']))
OUT.close()
print('ok')
