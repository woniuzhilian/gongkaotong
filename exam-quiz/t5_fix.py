# -*- coding: utf-8 -*-
"""T5: flip mis-mapped ':' -> '+' and ';' -> '-' inside math fragments.

Table R is hand-curated from _t5_cand.txt (all 274 candidate sites reviewed) and
cross-checked against the source PDF where possible.  --check validates every
literal occurrence count before anything is written.
"""
import os
import sys
import json
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
BAK = os.path.join(ROOT, '_fix_backup', 'questions_BEFORE_T5.json')
REP = os.path.join(ROOT, '_t5_fix.txt')

R = [
    (2, 'question', r'lim 2x^{2}:ax:b =1', r'lim 2x^{2}+ax+b =1', 1),
    (2, 'analysis', r'lim 2x^{2}:ax:b =lim 4x:a = 4:a =1', r'lim 2x^{2}+ax+b =lim 4x+a = 4+a =1', 1),
    (11, 'analysis', r'y(xz:1)$', r'y(xz+1)$', 1),
    (108, 'analysis', r'|;60|', r'|-60|', 1),
    (132, 'question', r'y =C e^{x}:C_{2}', r'y =C e^{x}+C_{2}', 1),
    (132, 'analysis', r'C e^{x}:C_{2} =', r'C e^{x}+C_{2} =', 1),
    (143, 'question', r'(Xi;X$)2', r'(Xi-X$)2', 1),
    (143, 'question', r'(Yi;Y$)2', r'(Yi-Y$)2', 1),
    (400, 'A', r' (:)', r' (+)', 1),
    (400, 'B', r' (;)', r' (-)', 1),
    (400, 'C', r'(:) (;)', r'(+) (-)', 1),
    (482, 'question', r'xf(x_{0} );x0f(x)', r'xf(x_{0} )-x0f(x)', 1),
    (482, 'question', r'x\rightarrow x_{0} x;x_{0}', r'x\rightarrow x_{0} x-x_{0}', 1),
    (606, 'question', r'sin2(x^{2}:1)', r'sin2(x^{2}+1)', 1),
    (606, 'B', r'2 sin(x^{2}:1)', r'2 sin(x^{2}+1)', 1),
    (606, 'analysis', r'sin2(x^{2}:1)', r'sin2(x^{2}+1)', 2),
    (613, 'question', r'\int ydx;xdy', r'\int ydx-xdy', 1),
    (613, 'question', r'x^{2}:y^{2}$值', r'x^{2}+y^{2}$值', 1),
    (655, 'A', r'(1;mch \theta)', r'(1-mch \theta)', 1),
    (655, 'B', r'(1;]im \theta)', r'(1-]im \theta)', 1),
    (655, 'C', r'(1;]im \theta)', r'(1-]im \theta)', 1),
    (655, 'D', r'(1;]im \theta)', r'(1-]im \theta)', 1),
    (733, 'question', r'(1,;1)', r'(1,-1)', 1),
    (733, 'analysis', r'(1,;1)', r'(1,-1)', 1),
    (844, 'analysis', r'x\rightarrow;\infty x\rightarrow:\infty', r'x\rightarrow-\infty x\rightarrow+\infty', 1),
    (852, 'analysis', r'f(\Delta x:0$,$1);f(0,1)', r'f(\Delta x+0$,$1)-f(0,1)', 1),
    (921, 'analysis', r'\sqrt1002:2002', r'\sqrt1002+2002', 1),
    (961, 'question', r'$x^{2}:1 -ax-b$', r'$x^{2}+1 -ax-b$', 1),
    (961, 'question', r'$x:1$', r'$x+1$', 1),
    (961, 'analysis', r'lim x^{2}:1 -ax-b =lim (1;a)x^{2};(a:b)x:1;b =\infty',
                     r'lim x^{2}+1 -ax-b =lim (1-a)x^{2}-(a+b)x+1-b =\infty', 1),
    (961, 'analysis', r'x\rightarrow\infty x:1 x:1$', r'x\rightarrow\infty x+1 x+1$', 1),
    (986, 'analysis', r'($T_{2};T_{1}$)', r'($T_{2}-T_{1}$)', 2),
    (986, 'analysis', r'($2 i :1$)', r'($2 i +1$)', 1),
    (1084, 'analysis', r'x\rightarrow:\infty x\rightarrow;\infty', r'x\rightarrow+\infty x\rightarrow-\infty', 1),
    (1108, 'A', r'RTM1;M2', r'RTM1-M2', 1),
    (1108, 'B', r'RT P1;P2', r'RT P1-P2', 1),
    (1108, 'C', r'RTM1;M2', r'RTM1-M2', 1),
    (1108, 'analysis', r'RTM1;M2', r'RTM1-M2', 1),
    (1108, 'analysis', r'V P1;P2', r'V P1-P2', 1),
    (1134, 'A', r'm1r_{1} 2: m2r_{2} 2', r'm1r_{1} 2+ m2r_{2} 2', 1),
    (1134, 'B', r'm1r_{1} 2: m2r_{2} 2', r'm1r_{1} 2+ m2r_{2} 2', 1),
    (1134, 'C', r'm1r_{1} : m2r_{2}', r'm1r_{1} + m2r_{2}', 1),
    (1134, 'D', r'm1r_{1} 2: m2r_{2} 2', r'm1r_{1} 2+ m2r_{2} 2', 1),
    (1267, 'analysis', r'M 2 :T 2', r'M 2 +T 2', 2),
    (1321, 'analysis', r'lim 1;\sqrt1;x =lim (1;x)2^{1}', r'lim 1-\sqrt1-x =lim (1-x)2^{1}', 1),
    (1321, 'analysis', r'\sqrt1;x x\rightarrow0(1;x)', r'\sqrt1-x x\rightarrow0(1-x)', 1),
    (1322, 'analysis', r'lim f(x);f(0) =lim ;3x:\alpha(x)', r'lim f(x)-f(0) =lim -3x+\alpha(x)', 1),
    (1330, 'A', r'f(x,0);f(0,0)', r'f(x,0)-f(0,0)', 1),
    (1330, 'A', r'f(0,y);f(0,0)', r'f(0,y)-f(0,0)', 1),
    (1330, 'B', r'f(x,y);f(0,0)', r'f(x,y)-f(0,0)', 1),
    (1330, 'C', r'\sqrt x^{2}:y^{2}', r'\sqrt x^{2}+y^{2}', 1),
    (1337, 'question', r'(x:y:z)', r'(x+y+z)', 1),
    (1337, 'analysis', r'=- 1:e;(x:y:z) =-1', r'=- 1+e;(x+y+z) =-1', 1),
    (1337, 'analysis', r'Fz 1:e;(x:y:z)', r'Fz 1+e;(x+y+z)', 1),
    (1337, 'analysis', r'(x:y:z)', r'(x+y+z)', 4),
    (1388, 'C', r'M y :M z', r'M y +M z', 1),
    (1388, 'analysis', r'M y 2:Mz 2', r'M y 2+Mz 2', 1),
    (1403, 'B', r'R1:R', r'R1+R', 1),
    (1403, 'B', r'R$2:\omega$L', r'R$2+\omega$L', 1),
    (1403, 'C', r'R_{1}:R_{2}', r'R_{1}+R_{2}', 1),
]


def load():
    return json.load(open(DB, encoding='utf-8'))


def simulate():
    """Return (ordered result dict, report lines, problems)."""
    data = load()
    byid = {q['id']: q for q in data}
    cur = {}
    rep, bad, hits = [], [], 0
    for tid, f, old, new, cnt in R:
        key = (tid, f)
        q = byid.get(tid)
        if q is None:
            bad.append('NO-QUESTION %s' % tid)
            continue
        if key not in cur:
            cur[key] = q.get(f) or ''
        v = cur[key]
        k = v.count(old)
        if k != cnt:
            bad.append('COUNT id=%s %s want=%d got=%d  %r' % (tid, f, cnt, k, old))
            continue
        if old.count('$') != new.count('$'):
            bad.append('$-DELIM-DRIFT id=%s %s  %r -> %r' % (tid, f, old, new))
            continue
        cur[key] = v.replace(old, new)
        hits += cnt
        rep.append('OK   id=%d %s x%d  - %s' % (tid, f, cnt, old))
        rep.append('                     + %s' % new)
    stats = '规则=%d 命中处=%d 异常=%d' % (len(R), hits, len(bad))
    rep.append(stats)
    for b in bad:
        rep.append('  !! ' + b)
    out = {}
    for (tid, f), v in cur.items():
        if v != (byid[tid].get(f) or ''):
            out.setdefault(tid, {})[f] = v
    return out, rep, bad


def main():
    changed, rep, bad = simulate()
    if '--check' in sys.argv:
        open(REP, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(rep))
        print('rules=%d bad=%d' % (len(R), len(bad)))
        return
    if bad:
        open(REP, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(rep))
        print('REFUSE: %d literal mismatches (see _t5_fix.txt)' % len(bad))
        return

    data = load()
    byid = {q['id']: q for q in data}
    before = open(DB, 'rb').read()
    rep.append('实改 题=%d 字段=%d' % (len(changed), sum(len(v) for v in changed.values())))
    for tid in sorted(changed):
        for f, nv in changed[tid].items():
            rep.append('---- id=%d [%s]' % (tid, f))
            rep.append('  - ' + byid[tid][f])
            rep.append('  + ' + nv)

    # post gates
    prob = []
    for q in data:
        for f in ('question', 'A', 'B', 'C', 'D', 'analysis'):
            v = q.get(f) or ''
            if v.count('$') % 2:
                prob.append('ODD-$ %s/%s' % (q['id'], f))
            if '$$' in v:
                prob.append('ADJACENT-$$ %s/%s' % (q['id'], f))
    rep.append('post校验问题=%d' % len(prob))
    rep.extend('  !! ' + p for p in prob[:40])
    open(REP, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(rep))
    if prob:
        print('REFUSE: post gates failed')
        return

    for tid, d in changed.items():
        for f, nv in d.items():
            byid[tid][f] = nv
    txt = json.dumps(data, ensure_ascii=False, indent=2)
    if '--dry' in sys.argv:
        open(os.path.join(ROOT, '_t5_new.json'), 'w', encoding='utf-8', newline='\r\n').write(txt)
        after = {str(t): d for t, d in sorted(changed.items())}
        before_sub = {str(t): {f: byid[t][f] for f in d} for t, d in sorted(changed.items())}
        for name, obj in (('_t5_changed.json', after), ('_t5_before.json', before_sub)):
            json.dump(obj, open(os.path.join(ROOT, name), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
        old_lines = before.decode('utf-8').replace('\r\n', '\n').split('\n')
        new_lines = txt.replace('\r\n', '\n').split('\n')
        print('DRY q=%d fields=%d lines old=%d new=%d' % (
            len(changed), sum(len(v) for v in changed.values()), len(old_lines), len(new_lines)))
        return

    if not os.path.isdir(os.path.dirname(BAK)):
        os.makedirs(os.path.dirname(BAK))
    if not os.path.exists(BAK):
        shutil.copy2(DB, BAK)
    with open(DB, 'w', encoding='utf-8', newline='\r\n') as fh:
        fh.write(txt)
    print('APPLIED q=%d fields=%d' % (len(changed), sum(len(v) for v in changed.values())))


if __name__ == '__main__':
    main()
