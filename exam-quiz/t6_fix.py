# -*- coding: utf-8 -*-
"""T6: repair '$' delimiter mis-splits.

The extractor sometimes opened a '$' at the start of a whole figure-bearing stem and
closed it at the end, so the renderer puts the Chinese sentence into math mode
(italic, re-spaced, KaTeX unicode warnings).  Other times a '$' leaked into an
<img style="..."> attribute and shifted every later pairing in the field.

This pass only MOVES '$' CHARACTERS.  It never edits, adds or deletes a single
non-'$' character, which is asserted by an invariant check (the field with all '$'
removed must be byte-identical before and after).  That keeps the pass independent
of the re-transcription work, where formula text itself has to be restored.
"""
import os
import re
import sys
import json
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
BAK = os.path.join(ROOT, '_fix_backup', 'questions_BEFORE_T6.json')
REP = os.path.join(ROOT, '_t6_fix.txt')
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']

HAN = r'㐀-䶿一-鿿'
CJK = re.compile('[' + HAN + '，。；：、（）％]')
TAG = re.compile(r'<\s*(/?)(img|br|hr|a|math)\b[^>]*>', re.I)
MATHISH = re.compile(r'[\\^_]')


def split_tags(t):
    """[(text, is_tag), ...] covering the whole string."""
    out, i = [], 0
    for m in TAG.finditer(t):
        if m.start() > i:
            out.append((t[i:m.start()], False))
        out.append((m.group(0), True))
        i = m.end()
    if i < len(t):
        out.append((t[i:], False))
    return out


ARGCMD = (r'frac|dfrac|tfrac|binom|sqrt|vec|bm|hat|tilde|widetilde|widehat|bar|overline|'
          r'underline|dot|ddot|acute|grave|check|breve|mathbb|mathbf|mathrm|mathcal|'
          r'mathit|mbox|hbox|text|textrm|textit|stackrel|overset|underset|begin|end|'
          r'left|right|overrightarrow|raisebox')
DANGLE_TAIL = re.compile(r'(?:[_\^&\\{]$|\\(?:' + ARGCMD + r')$)')
DANGLE_HEAD = re.compile(r'^(?:[_\^&}]|^\\end)')


def run_ok(s):
    if s.count('{') != s.count('}'):
        return False
    if len(re.findall(r'\\begin\{', s)) != len(re.findall(r'\\end\{', s)):
        return False
    if DANGLE_TAIL.search(s) or DANGLE_HEAD.search(s):
        return False
    return True


def plan_runs(piece):
    """Re-delimited text for a mis-split fragment, or None to leave it alone."""
    if re.search(r'\\(?:text|mbox|textrm|textit|begin|end)\b', piece):
        return None
    segs, i = [], 0
    for m in CJK.finditer(piece):
        segs.append((piece[i:m.start()], False))
        segs.append((m.group(0), True))
        i = m.end()
    segs.append((piece[i:], False))
    cand = [s.strip() for s, cjk in segs if not cjk and s.strip() and MATHISH.search(s)]
    if not all(run_ok(c) for c in cand):
        return None
    out = []
    for s, cjk in segs:
        if cjk:
            out.append(s)
            continue
        t = s.strip()
        if t and MATHISH.search(t):
            out.append(s[:len(s) - len(s.lstrip())] + '$' + t + '$' + s[len(s.rstrip()):])
        else:
            out.append(s)
    return ''.join(out)


def fix_field(v):
    note = []
    for tag, is_tag in split_tags(v):
        if is_tag and '$' in tag:
            note.append('HTML内$%d个已删' % tag.count('$'))
    v = ''.join(t.replace('$', '') if tg else t for t, tg in split_tags(v))

    out, i = [], 0
    while True:
        a = v.find('$', i)
        if a < 0:
            out.append(v[i:])
            break
        b = v.find('$', a + 1)
        if b < 0:
            out.append(v[i:])
            note.append('落单$')
            break
        frag = v[a + 1:b]
        out.append(v[i:a])
        new = plan_runs(frag) if CJK.search(frag) else None
        if new is not None:
            note.append('重切@%d' % a)
            out.append(new)
        else:
            if CJK.search(frag):
                note.append('放弃@%d' % a)
            out.append(v[a:b + 1])
        i = b + 1
    return ''.join(out), note


def scan_fields(data):
    for q in data:
        for f in FIELDS:
            v = q.get(f)
            if isinstance(v, str) and '$' in v:
                yield q['id'], f, v


def main():
    data = json.load(open(DB, encoding='utf-8'))
    changed, notes, skipped, refused, fatal = {}, [], [], [], []
    for tid, f, v in scan_fields(data):
        nv, nt = fix_field(v)
        refused += ['id=%d %s %s' % (tid, f, x) for x in nt if x.startswith('放弃')]
        if nv == v:
            continue
        if re.sub(r'\$', '', nv) != re.sub(r'\$', '', v):
            fatal.append('INVARIANT id=%d %s' % (tid, f))
            continue
        if '$$' in nv or nv.count('$') % 2:
            skipped.append('SHAPE id=%d %s  %r' % (tid, f, nv[:80]))
            continue
        changed.setdefault(tid, {})[f] = nv
        notes.append('id=%d %s  %s' % (tid, f, '; '.join(nt)))

    rep = ['修复字段=%d 题=%d 形状放弃字段=%d 片段放弃重切=%d 致命=%d' % (
        sum(len(v) for v in changed.values()), len(changed), len(skipped), len(refused), len(fatal))]
    rep += ['  .. ' + r for r in refused]
    rep += ['  .. ' + s for s in skipped]
    rep += ['  !! ' + s for s in fatal]
    rep.append('')
    byid = {q['id']: q for q in data}
    for tid in sorted(changed):
        for f, nv in changed[tid].items():
            rep.append('---- id=%d %s' % (tid, f))
            rep.append('  - ' + byid[tid][f])
            rep.append('  + ' + nv)
    open(REP, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(rep))

    before_sub = {str(t): {f: byid[t][f] for f in d} for t, d in sorted(changed.items())}
    json.dump(before_sub, open(os.path.join(ROOT, '_t6_before.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump({str(t): d for t, d in sorted(changed.items())},
              open(os.path.join(ROOT, '_t6_changed.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('fields=%d q=%d skipped=%d' % (
        sum(len(v) for v in changed.values()), len(changed), len(skipped)))
    if '--apply' not in sys.argv:
        return
    if fatal:
        print('REFUSE: %d 个字段未通过文本不变量检查' % len(fatal))
        return
    for q in data:
        for f, nv in changed.get(q['id'], {}).items():
            q[f] = nv
    txt = json.dumps(data, ensure_ascii=False, indent=2)
    if not os.path.isdir(os.path.dirname(BAK)):
        os.makedirs(os.path.dirname(BAK))
    if not os.path.exists(BAK):
        shutil.copy2(DB, BAK)
    with open(DB, 'w', encoding='utf-8', newline='\r\n') as fh:
        fh.write(txt)
    print('APPLIED')


if __name__ == '__main__':
    main()
