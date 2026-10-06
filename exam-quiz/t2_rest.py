# -*- coding: utf-8 -*-
"""T2 应用后残余画像：把 formula_tiers 的 T2 命中点按 base 类型分桶"""
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
OPS = set('times cdot pm mp div angle degree langle rangle'
          .split(' '))
CAND = re.compile('((?:' + B + B + '[A-Za-z]+)|[A-Za-z])([0-9]{1,3})(?![0-9A-Za-z.])')
T2MASK1 = re.compile(B + B + '[a-zA-Z]+')


def mask(inner):
    """复刻 formula_tiers.cjs 的 T2 判据：掩掉已知命令与已有上下标"""
    s = T2MASK1.sub(lambda mm: (chr(1) * len(mm.group(0))) if mm.group(0)[1:] in CMD else mm.group(0), inner)
    s = re.sub('[_^]' + B + '[{][^{}]*[}]', chr(2), s)
    s = re.sub('[_^]' + B + 'd', chr(2), s)
    return s

data = json.load(io.open(DB, encoding='utf-8'))
buckets = collections.Counter()
tokn = collections.Counter()
qhas = {'A': set(), 'B': set(), 'C': set()}
tierT2 = set()

for q in data:
    tid = q['id']
    for f in FIELDS:
        t = q.get(f) or ''
        if not t:
            continue
        for m in re.finditer(r'\$([^$]+)\$', t):
            inner = m.group(1)
            s = mask(inner)
            if re.search('([A-Za-z])([0-9]{1,3})(?![0-9A-Za-z.])', s):
                tierT2.add(tid)
            for mm in CAND.finditer(inner):
                base, dig = mm.group(1), mm.group(2)
                if base[0] == B:
                    cmd = base[1:]
                    if cmd in OPS:
                        k = 'C'
                    elif cmd in CMD:
                        k = 'B'
                    else:
                        k = 'C'
                else:
                    k = 'A'
                buckets[k] += 1
                tokn[k + ' ' + base + dig] += 1
                qhas[k].add(tid)

out = []
out.append('formula_tiers 口径 T2 题数=%d' % len(tierT2))
out.append('A 纯字母+数字（真上下标候选）: 处=%d 题=%d' % (buckets['A'], len(qhas['A'])))
out.append('B 变量命令+数字（希腊字母等，真候选）: 处=%d 题=%d' % (buckets['B'], len(qhas['B'])))
out.append('C 运算符/未知命令+数字（times2、angle45 这类，不该改）: 处=%d 题=%d' % (buckets['C'], len(qhas['C'])))
out.append('')
out.append('===== A 桶残余 token TOP 30 =====')
for k, n in sorted([x for x in tokn.items() if x[0].startswith('A ')], key=lambda y: -y[1])[:30]:
    out.append('  %s x%d' % (k[2:], n))
out.append('===== B 桶残余 token TOP 20 =====')
for k, n in sorted([x for x in tokn.items() if x[0].startswith('B ')], key=lambda y: -y[1])[:20]:
    out.append('  %s x%d' % (k[2:], n))
out.append('===== C 桶 token TOP 15 =====')
for k, n in sorted([x for x in tokn.items() if x[0].startswith('C ')], key=lambda y: -y[1])[:15]:
    out.append('  %s x%d' % (k[2:], n))
ab = qhas['A'] | qhas['B']
out.append('')
out.append('含 A/B 真候选的题数=%d，其中仅A或仅B: A_only=%d B_only=%d' % (len(ab), len(qhas['A'] - qhas['B']), len(qhas['B'] - qhas['A'])))
onlyC = qhas['C'] - ab
out.append('只有 C 桶（可判为检测器误报，无需修）的题数=%d' % len(onlyC))
out.append('A/B 题号: %s' % ' '.join(str(i) for i in sorted(ab)))
io.open(os.path.join(ROOT, '_t2_rest.txt'), 'w', encoding='utf-8', newline='\r\n').write('\n'.join(out))
print('T2tier=%d A=%d B=%d C=%d onlyC=%d' % (len(tierT2), len(qhas['A']), len(qhas['B']), len(qhas['C']), len(onlyC)))
