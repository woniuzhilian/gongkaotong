# -*- coding: utf-8 -*-
import json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

PATH = r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
qs = json.load(open(PATH, encoding='utf-8'))
print("total:", len(qs))
print("keys:", list(qs[0].keys()))
print(collections.Counter(q.get('bigSubject') for q in qs))

def has_cjk(s):
    return bool(re.search(r'[\u4e00-\u9fff]', s or ''))

# 1) 空字段
fields = ['question','A','B','C','D','answer','analysis']
for f in fields:
    empties = [q['id'] for q in qs if not str(q.get(f,'')).strip()]
    print(f"\n[{f}] empty count={len(empties)} ids={empties[:40]}")

# 2) 空选项（B/C/D 或 A 为空）
opt_empty = []
for q in qs:
    empty_opts = [o for o in 'ABCD' if not str(q.get(o,'')).strip()]
    if empty_opts:
        opt_empty.append((q['id'], ''.join(empty_opts), q.get('year'), q.get('bigSubject')))
print(f"\n[empty options] count={len(opt_empty)}")
for e in opt_empty:
    print("   ", e)
