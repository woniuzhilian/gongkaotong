# -*- coding: utf-8 -*-
"""残余 T2 归因：与提案覆盖交叉，按题别/定位情况分桶"""
import os, re, io, json, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
B = chr(92)
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']
CMD = set(('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi pi rho sigma tau upsilon phi chi psi omega '
           'Gamma Delta Theta Lambda Xi Pi Sigma Phi Psi Omega sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh log ln lg exp lim max min det '
           'int sum prod oint iint iiint sqrt frac dfrac tfrac binom leq geq neq approx infty cdots ldots dots rightarrow leftarrow Rightarrow Leftarrow '
           'Leftrightarrow to mapsto sim simeq equiv partial nabla in notin subset supset cup cap emptyset forall exists mathrm mathbf mathbb mathcal '
           'text operatorname begin end cases matrix pmatrix left right big overline underline hat bar vec dot ddot tilde circ').split(' '))
VARCMD = set('alpha beta gamma delta epsilon varepsilon zeta eta theta iota kappa lambda mu nu xi pi rho sigma tau upsilon phi varphi chi psi omega '
             'Gamma Delta Theta Lambda Xi Pi Sigma Phi Psi Omega'.split(' '))
M1 = re.compile(B + B + '[a-zA-Z]+')
CAND = re.compile('((?:' + B + B + '[A-Za-z]+)|[A-Za-z])([0-9])(?![0-9A-Za-z.])')


def mask(inner):
    s = M1.sub(lambda mm: (chr(1) * len(mm.group(0))) if mm.group(0)[1:] in CMD else mm.group(0), inner)
    s = re.sub('[_^]' + B + '[{][^{}]*[}]', chr(2), s)
    s = re.sub('[_^]' + B + 'd', chr(2), s)
    return s


data = json.load(io.open(DB, encoding='utf-8'))
edits = json.load(io.open(os.path.join(ROOT, '_t2_edits.json'), encoding='utf-8'))
prop_txt = io.open(os.path.join(ROOT, '_t2_prop.txt'), encoding='utf-8').read()
located = set(int(m.group(1)) for m in re.finditer('id=(\\d+)', prop_txt))
nopair = set()
for m in re.finditer('id=(\\d+) [^ ]+ .*原书无此配对', prop_txt):
    nopair.add(int(m.group(1)))

rows = collections.Counter()
sites = collections.Counter()
gap_ids = collections.defaultdict(list)
for q in data:
    tid, big = q['id'], q['bigSubject']
    hitA = hitG = False
    for f in FIELDS:
        t = q.get(f) or ''
        for m in re.finditer(r'\$([^$]+)\$', t):
            if re.search('([A-Za-z])([0-9])(?![0-9A-Za-z.])', mask(m.group(1))):
                hitA = True
            for mm in CAND.finditer(m.group(1)):
                base = mm.group(1)
                if base[0] == B and base[1:] in VARCMD:
                    hitG = True
    if not (hitA or hitG):
        continue
    if hitA and big == '公共基础':
        k = '公共基础-有字母+数字残点'
    elif hitA:
        k = '专业基础-有字母+数字残点'
    else:
        k = '仅希腊命令+数字'
    rows[k] += 1
    if str(tid) in edits:
        rows[k + ' |本轮已部分修复'] += 1
    elif tid in located:
        rows[k + ' |定位到但无配对'] += 1
    else:
        rows[k + ' |两书未定位'] += 1
    gap_ids[k].append(tid)

out = []
for k in sorted(rows):
    out.append('%-40s %d' % (k, rows[k]))
out.append('')
out.append('说明: formula_tiers 的 T2 判据只认“字母+恰好1位数字”，多位数(如 x100)不在其口径内')
io.open(os.path.join(ROOT, '_t2_gap.txt'), 'w', encoding='utf-8', newline='\r\n').write('\n'.join(out))
print('\n'.join(out).encode('unicode_escape').decode()[:1200])
