# -*- coding: utf-8 -*-
"""T6 scan v2 — precise '$' mis-split census.

v1 false positives fixed here:
  * '$L$' style single-token fragments are legitimate math, not mis-splits;
  * '<' is very often a math less-than sign, so HTML detection must anchor on
    real tag names only.
"""
import os
import re
import json
import collections

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
OUT = os.path.join(ROOT, '_t6_scan.txt')
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']

HAN = re.compile(r'[㐀-䶿一-鿿]')
CPUN = re.compile(r'[，。；：、（）％]')
TAG = re.compile(r'<\s*(/?)(img|br|hr|a|sup|sub|b|i|u|em|strong|div|span|p|font|table|tr|td)\b[^>]*>', re.I)
CJK_RUN = re.compile(r'(?:[㐀-䶿一-鿿，。；：、（）]|\s)+')


def spans(t):
    out, i = [], 0
    while True:
        a = t.find('$', i)
        if a < 0:
            break
        b = t.find('$', a + 1)
        if b < 0:
            out.append((None, a, -1))
            break
        out.append((t[a + 1:b], a, b))
        i = b + 1
    return out


def judge(frag):
    """Classify a paired fragment. Returns None when it is fine."""
    if not HAN.search(frag) and not CPUN.search(frag):
        return None
    cjk = len(HAN.findall(frag))
    tot = len(re.sub(r'\s', '', frag))
    if not tot:
        return None
    if cjk == 0:                       # only full-width punctuation, e.g. $，$
        return 'P'
    if cjk * 100 // max(tot, 1) >= 40:
        return 'PROSE'                  # mostly prose -> an opening/closing $ is wrong
    return 'MIXED'                      # formula + a few stray Chinese chars


def main():
    data = json.load(open(DB, encoding='utf-8'))
    rows = []
    st = collections.Counter()
    for q in data:
        tid = q['id']
        for f in FIELDS:
            v = q.get(f) or ''
            if '$' not in v:
                continue
            odd = v.count('$') % 2
            tags = [m.group(0) for m in TAG.finditer(v)]
            htd = [g for g in tags if '$' in g]
            bad = []
            for frag, a, b in spans(v):
                if frag is None:
                    bad.append(('UNPAIRED', a, v[a:a + 60]))
                    continue
                k = judge(frag)
                if k:
                    lead = CJK_RUN.match(frag)
                    trail = CJK_RUN.search(frag[::-1])
                    side = 'HEAD' if (lead and trail and lead.start() == 0 and lead.end() == len(frag)) else (
                        'HEAD' if (lead and lead.start() == 0) else 'TAIL' if (trail and trail.start() == 0) else 'MID')
                    bad.append((k + '/' + side, a, v[max(0, a - 12):b + 13]))
            if not bad and not htd and not odd:
                continue
            rows.append((tid, f, odd, htd, bad, v))
            st['fields'] += 1
            st['questions'] += 0
            if odd:
                st['ODD'] += 1
            if htd:
                st['HTML$'] += len(htd)
            for k in bad:
                st[k[0].split('/')[0]] += 1
                st[k[0]] += 1

    rep = []
    rep.append('受影响字段=%d  题数=%d' % (st['fields'], len({r[0] for r in rows})))
    for k in ('ODD', 'HTML$', 'UNPAIRED', 'PROSE', 'MIXED', 'P'):
        rep.append('  %-9s = %d' % (k, st[k]))
    rep.append('  PROSE 细分: ' + ', '.join('%s=%d' % (k.split('/')[1], st[k])
                                            for k in st if k.startswith('PROSE/')))
    rep.append('  MIXED 细分: ' + ', '.join('%s=%d' % (k.split('/')[1], st[k])
                                            for k in st if k.startswith('MIXED/')))
    rep.append('')
    rep.append('===== HTML 标签内混入 $ （机械可修）=====')
    for tid, f, odd, htd, bad, v in rows:
        for g in htd:
            rep.append('id=%d %s  %s' % (tid, f, g))
    rep.append('')
    rep.append('===== PROSE（整段中文被吞进公式）=====')
    for tid, f, odd, htd, bad, v in rows:
        pb = [b for b in bad if b[0].startswith('PROSE')]
        if not pb:
            continue
        rep.append('---- id=%d %s dollars=%d' % (tid, f, v.count('$')))
        rep.append('  FULL %s' % v[:330])
        for k, a, s in pb:
            rep.append('   %s @%-4d %s' % (k, a, s[:170]))
    rep.append('')
    rep.append('===== MIXED（公式里夹少量汉字）=====')
    for tid, f, odd, htd, bad, v in rows:
        mb = [b for b in bad if b[0].startswith('MIXED') or b[0].startswith('P/') or b[0] == 'UNPAIRED']
        if not mb:
            continue
        rep.append('---- id=%d %s dollars=%d' % (tid, f, v.count('$')))
        for k, a, s in mb:
            rep.append('   %s @%-4d %s' % (k, a, s[:170]))
    open(OUT, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(rep))
    print('fields=%d q=%d ODD=%d HTML$=%d PROSE=%d MIXED=%d P=%d UNPAIRED=%d' % (
        st['fields'], len({r[0] for r in rows}), st['ODD'], st['HTML$'],
        st['PROSE'], st['MIXED'], st['P'], st['UNPAIRED']))


if __name__ == '__main__':
    main()
