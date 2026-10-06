# 把 PDF 量测结论映射回题库字段的具体字符位置, 生成可审阅的逐站点改写计划
# 与 t2_scan.cjs 使用同一套等长掩码 + 同一命中正则, 逐条重放以保证站点<->位置 1:1
import json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.abspath(__file__))
DB = json.load(open(os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json'), encoding='utf-8'))
SITES = json.load(open(os.path.join(ROOT, '_t2_sites.json'), encoding='utf-8'))
VERD = json.load(open(os.path.join(ROOT, '_t2_verdicts.json'), encoding='utf-8'))
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']

CMDS = set(('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi pi rho sigma tau '
            'upsilon phi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Phi Psi Omega varepsilon '
            'varsigma varphi vartheta sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh log ln '
            'lg exp lim max min det gcd int sum prod oint iint iiint sqrt frac dfrac tfrac binom leq geq '
            'neq approx infty cdots ldots dots rightarrow leftarrow Rightarrow Leftarrow Leftrightarrow to '
            'mapsto sim simeq equiv partial nabla in notin subset supset cup cap emptyset forall exists '
            'mathrm mathbf mathbb mathcal mathit text mbox operatorname begin end cases matrix pmatrix '
            'left right big Big bigg Bigg overline underline hat bar vec dot ddot tilde widetilde '
            'widehat circ odot oplus otimes lbrace rbrace').split(' '))


def mask(frag):
    s = re.sub(r'\\[a-zA-Z]+', lambda m: '#' * len(m.group(0))
               if (m.group(0)[1:] in CMDS or m.group(0)[1:].isalpha()) else m.group(0), frag)
    s = re.sub(r'[_^]\{[^{}]*\}', lambda m: '#' * len(m.group(0)), s)
    s = re.sub(r'[_^][A-Za-z0-9]', '##', s)
    return s


HIT = re.compile(r'([A-Za-z])(\d{1,2})(?![\dA-Za-z])')


def regen(q):
    """按 t2_scan.cjs 的枚举顺序重放该题的站点, 附带字母在字段中的绝对下标"""
    out = []
    for f in FIELDS:
        t = q.get(f) or ''
        if not t:
            continue
        for m in re.finditer(r'\$([^$]+)\$', t):
            frag, base = m.group(1), m.start() + 1
            for h in HIT.finditer(mask(frag)):
                out.append({'f': f, 'frag': frag, 'i': h.start(), 'letter': h.group(1),
                            'digits': h.group(2), 'pos': base + h.start()})
    return out


def nospace(s):
    return re.sub(r'\s+', '', s or '')


def suffix(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[len(a) - 1 - n] == b[len(b) - 1 - n]:
        n += 1
    return n


def prefix(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


def flags_of(p):
    fl = []
    if not p['ok_pos']:
        fl.append('POS!')
    if p['v'] == 'SUP' and p['digits'] == '1':
        fl.append('SUP1')
    if p['v'] == 'SUP' and p['digits'][-1] in '01':
        fl.append('END01')
    if p['letter'] in 'WwOo':
        fl.append('LTR=' + p['letter'])
    if (p['dba'] or '').startswith('/') or (p['pga'] or '').startswith('/'):
        fl.append('FRAC')
    if p['score'] < 4:
        fl.append('LOWSC=%s' % p['score'])
    if not p['lig'] and (p['dbyem'] is None or abs(p['dbyem']) < 0.25):
        fl.append('SHALLOW=%s' % p['dbyem'])
    if p['csuf'] < 3 and p['cpre'] < 2:
        fl.append('PDFCTX')
    return fl


plan = []
k = 0
from collections import Counter
NSC = Counter(s['id'] for s in SITES)
for q in DB:
    rs = regen(q)
    n = NSC.get(q['id'], 0)
    assert len(rs) == n, 'site count mismatch id=%s %d vs %d' % (q['id'], len(rs), n)
    for r in rs:
        s, v = SITES[k], VERD[k]
        k += 1
        assert s['id'] == q['id'] and s['f'] == r['f'] and s['i'] == r['i'] \
            and s['letter'] == r['letter'] and s['digits'] == r['digits'], (s, r)
        field = q[r['f']]
        old = r['letter'] + r['digits']
        sm = (v.get('sample') or [{}])[0]
        pb, pa = sm.get('before') or '', sm.get('after') or ''
        db_b = nospace(field[max(0, r['pos'] - len(pb) - 4):r['pos']])
        db_a = nospace(field[r['pos'] + len(old):r['pos'] + len(old) + len(pa) + 4])
        ls = sm.get('lsize')
        p = dict(id=q['id'], big=q['bigSubject'], f=r['f'], pos=r['pos'], i=r['i'],
                 letter=r['letter'], digits=r['digits'], old=old, frag=r['frag'],
                 v=v['v'], score=v.get('score', 0),
                 ok_pos=field[r['pos']:r['pos'] + len(old)] == old,
                 path=v.get('path'), pages=v.get('pages'),
                 dy=sm.get('dy'), ratio=sm.get('ratio'), lig=sm.get('lig'),
                 lsize=ls, dsize=sm.get('dsize'), pgb=pb, pga=pa,
                 dbb=db_b[-8:], dba=db_a[:8],
                 csuf=suffix(db_b, pb), cpre=prefix(db_a, pa),
                 dbyem=(round(sm['dy'] / ls, 3) if (sm.get('dy') is not None and ls) else None),
                 ctx=field[max(0, r['pos'] - 16):r['pos'] + len(old) + 16])
        p['flags'] = flags_of(p)
        plan.append(p)

assert k == len(SITES) == len(VERD), (k, len(SITES), len(VERD))
json.dump(plan, open(os.path.join(ROOT, '_t2_plan.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

keep = [p for p in plan if p['v'] in ('SUP', 'SUB')]
L = ['SUP/SUB 站点=%d 题数=%d' % (len(keep), len(set(p['id'] for p in keep)))]
for p in sorted(keep, key=lambda x: (x['id'], x['f'], x['pos'])):
    neu = p['letter'] + ('^' if p['v'] == 'SUP' else '_') + '{' + p['digits'] + '}'
    L.append('id=%-5s %-8s %-4s -> %-10s %-3s sc=%-2s dyem=%-7s ratio=%-5s lig=%-1s cs=%d/%d %s'
             % (p['id'], p['f'], p['old'], neu, p['v'], p['score'], p['dbyem'], p['ratio'],
                bool(p['lig']), p['csuf'], p['cpre'],
                ('!!' + ','.join(p['flags'])) if p['flags'] else 'CLEAN'))
    L.append('      pdf  %s <<%s>> %s' % (json.dumps(p['pgb'], ensure_ascii=False), p['old'],
                                          json.dumps(p['pga'], ensure_ascii=False)))
    L.append('      db   %s <<%s>> %s' % (json.dumps(p['dbb'], ensure_ascii=False), p['old'],
                                          json.dumps(p['dba'], ensure_ascii=False)))

clean = [p for p in keep if not p['flags'] and p['ok_pos'] and p['score'] >= 4
         and (p['lig'] or abs(p['dbyem'] or 0) >= 0.25) and (p['csuf'] >= 3 or p['cpre'] >= 2)]
json.dump(clean, open(os.path.join(ROOT, '_t2_clean.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(ROOT, '_t2_plan.txt'), 'w', encoding='utf-8').write('\n'.join(L))

from collections import Counter
cnt = Counter()
for p in keep:
    for fl in p['flags']:
        cnt[fl.split('=')[0]] += 1
print('sup/sub=%d clean=%d clean_q=%d' % (len(keep), len(clean), len(set(p['id'] for p in clean))))
print('flag统计:', dict(cnt))
