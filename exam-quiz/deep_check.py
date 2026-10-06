import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

# 检查OCR残留 ===PAGE_XXX===
print("="*60)
print("OCR残留检查 (===PAGE_XXX===)")
print("="*60)

for name, filepath in [
    ('公共基础', r'D:\应用程序开发\刷题\all_questions_final.json'),
    ('专业基础', r'D:\应用程序开发\刷题\prof_questions_final_v2.json')
]:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    page_residual = []
    for q in data:
        for field in ['question', 'A', 'B', 'C', 'D', 'analysis']:
            val = q.get(field, '')
            if '===PAGE' in val or '===' in val:
                page_residual.append((q['id'], field, val[:80]))
    
    print(f"\n{name}: {len(page_residual)}处OCR残留")
    for qid, field, val in page_residual[:10]:
        print(f"  id={qid}, {field}: {val}")

# 检查公共基础空选项的具体情况
print("\n" + "="*60)
print("公共基础空选项详细分析")
print("="*60)

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    pub = json.load(f)

empty_opt_by_year = {}
for q in pub:
    empty_opts = [opt for opt in ['A', 'B', 'C', 'D'] if q[opt] == '']
    if empty_opts:
        year = q['year']
        if year not in empty_opt_by_year:
            empty_opt_by_year[year] = []
        empty_opt_by_year[year].append((q['id'], empty_opts, q['question'][:50]))

for year in sorted(empty_opt_by_year.keys()):
    items = empty_opt_by_year[year]
    print(f"\n{year}: {len(items)}道题")
    for qid, opts, q in items[:3]:
        print(f"  id={qid}, 空选项={opts}, 题干={q}")

# 检查LaTeX公式问题
print("\n" + "="*60)
print("LaTeX公式格式检查")
print("="*60)

latex_issues = []
for q in pub:
    text = q['question'] + q['analysis']
    # 检查$数量是否为偶数
    if text.count('$') % 2 != 0:
        latex_issues.append((q['id'], 'question/analysis', '$未配对'))
    # 检查公式中是否有换行或异常
    for m in re.finditer(r'\$[^$]{0,5}\n[^$]*\$', text):
        latex_issues.append((q['id'], '公式内换行', m.group(0)[:50]))

print(f"公共基础LaTeX问题: {len(latex_issues)}处")
for qid, issue, val in latex_issues[:10]:
    print(f"  id={qid}, {issue}: {val}")
