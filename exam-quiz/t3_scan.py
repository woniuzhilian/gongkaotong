# -*- coding: utf-8 -*-
"""T3 符号错映射：全量清点（含上下文），输出 _t3_scan.txt"""
import os, re, json, io

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
data = json.load(open(DB, encoding='utf-8'))
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']
B = chr(92)          # 单个反斜杠
BB = chr(92) * 2     # 正则里的字面反斜杠

RULES = [
    ('varsigma', BB + 'varsigma', '应为 sigma'),
    ('epsilon', BB + 'epsilon(?!\\w)', '应为 varepsilon'),
    ('cdots', BB + 'cdots', '疑应为 cdot'),
    ('Theta', BB + 'Theta', '疑应为 ominus'),
    ('square', BB + 'square', '不可渲染字形'),
]

out = io.open(os.path.join(ROOT, '_t3_scan.txt'), 'w', encoding='utf-8')
stat = {}
for q in data:
    for f in FIELDS:
        t = str(q.get(f) or '')
        if not t:
            continue
        for name, pat, note in RULES:
            for m in re.finditer(pat, t):
                a, b2 = max(0, m.start() - 26), min(len(t), m.end() + 26)
                stat.setdefault(name, []).append((q['id'], f, t[a:b2]))
tot = 0
for name, pat, note in RULES:
    lst = stat.get(name, [])
    ids = sorted(set(i for i, _, _ in lst))
    tot += len(ids)
    out.write('===== %s (%s) 命中 %d 处 / %d 题: %s\n' % (name, note, len(lst), len(ids), ids))
    for i, f, ctx in lst:
        out.write('   id=%-5s %-9s ...%s...\n' % (i, f, ctx.replace('\n', ' ')))
out.write('\n各规则题数相加=%d（可能重复计题）\n' % tot)
allids = sorted(set(i for v in stat.values() for i, _, _ in v))
out.write('去重后涉及题数=%d\n' % len(allids))
out.write('%s\n' % allids)
out.close()
print('occ=%d q=%d' % (sum(len(v) for v in stat.values()), len(allids)))
