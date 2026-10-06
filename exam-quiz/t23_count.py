# -*- coding: utf-8 -*-
"""重算 T2（上下标塌陷）/ T3（符号错映射）在题干+选项+解析中的剩余题数"""
import os, re, json, io

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
data = json.load(open(DB, encoding='utf-8'))
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']
D = '[$]'

BS = chr(92) * 2
T3 = {
    BS + 'varsigma': 'varsigma(应为sigma)',
    BS + 'epsilon': 'epsilon(应为varepsilon)',
    BS + 'square': 'square(不可渲染字形)',
    BS + 'theta[a-z]': 'theta与后续命令粘连',
}
T2 = {
    r'[a-zA-Z' + D + r'\)\]]\d\d?[a-zA-Z' + D + r']': '字母后紧跟数字(疑上下标丢失)',
    r'\d' + D + r'_' + D + r'\d': '下标断裂',
}
cnt3, cnt3q, cnt2 = {}, set(), set()
ex2 = []
for q in data:
    for f in FIELDS:
        t = str(q.get(f) or '')
        if not t:
            continue
        for pat, name in T3.items():
            if re.search(pat, t):
                cnt3.setdefault(name, set()).add(q['id'])
                cnt3q.add(q['id'])
        for pat, name in T2.items():
            if re.search(pat, t):
                cnt2.add(q['id'])
                if len(ex2) < 25:
                    m = re.search(pat, t)
                    ex2.append((q['id'], f, t[max(0, m.start() - 18):m.end() + 18]))

out = io.open(os.path.join(ROOT, '_t23_left.txt'), 'w', encoding='utf-8')
out.write('题库=%d 题\n' % len(data))
out.write('T3 符号错映射 剩余题数=%d\n' % len(cnt3q))
for k, v in sorted(cnt3.items(), key=lambda x: -len(x[1])):
    out.write('   %-30s %3d 题  列前12: %s\n' % (k, len(v), sorted(v)[:12]))
out.write('T2 上下标塌陷(粗规则) 命中题数=%d\n' % len(cnt2))
for e in ex2:
    out.write('   id=%-5s %-9s %s\n' % e)
out.close()
print('ok')
