# -*- coding: utf-8 -*-
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
PATH = r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
qs = json.load(open(PATH, encoding='utf-8'))

FIELDS = ['question','A','B','C','D','analysis']
def dollar_odd(s):
    return (s or '').count('$') % 2 == 1

# 1) 各字段 $ 数量为奇数（KaTeX 无法配对渲染）
for f in FIELDS:
    hits = [q['id'] for q in qs if dollar_odd(q.get(f,''))]
    print(f"[{f}] '$'奇数 count={len(hits)} {hits[:50]}")

# 2) 含 LaTeX 控制符但无 $ 包裹（可能漏了 $）
ctrl = re.compile(r'\\(times|cdot|alpha|beta|theta|sigma|epsilon|varphi|mu|pi|lambda|Delta|sum|int|frac|sqrt|circ|pm|leq|geq|neq|rightarrow|infty|approx)')
for f in FIELDS:
    hits = [q['id'] for q in qs if ctrl.search(str(q.get(f,''))) and (q.get(f,'').count('$')%2==1)]
    print(f"[{f}] 控制符+$奇数 count={len(hits)} {hits[:40]}")

# 3) 疑似 OCR 损坏：出现 "数字:字母" 或 "字母:数字" 粘连（分数/比号错位）
ocr = re.compile(r'[0-9A-Za-z]\s*[:：]\s*[0-9A-Za-z]')
# 4) 出现 \circ 错用来表示角度
deg = re.compile(r'\\circ')
print()
for f in FIELDS:
    hits=[q['id'] for q in qs if re.search(r'\\cdotm|\\cdot m', str(q.get(f,'')))]
    if hits: print(f"[{f}] \\cdotm 非法 {len(hits)} {hits[:20]}")

# 5) 选项仅 A 有图，B/C/D 空（图示选项题）
imgA = [q['id'] for q in qs if '<img' in str(q.get('A','')) and not q.get('B','').strip() and not q.get('C','').strip() and not q.get('D','').strip()]
print(f"\n[仅A有图 BCD空] {len(imgA)} {imgA}")

# 6) 题干极短
shortq=[(q['id'],q['question']) for q in qs if len(q['question'].strip())<12]
print(f"\n[题干<12字] {len(shortq)}")
for s in shortq: print("   ",s)
