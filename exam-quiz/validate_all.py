import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

def validate_questions(filepath, name):
    print(f"\n{'='*60}")
    print(f"校验: {name}")
    print(f"文件: {filepath}")
    print(f"{'='*60}")
    
    errors = []
    warnings = []
    
    # 1. JSON语法
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"\n[1] JSON语法: 合法，共{len(data)}道题")
    except json.JSONDecodeError as e:
        errors.append(f"JSON语法错误: {e}")
        print(f"\n[1] JSON语法: 错误 - {e}")
        return errors, warnings
    
    # 2. answer字段
    invalid_answer = []
    empty_answer = []
    for q in data:
        ans = q.get('answer', '')
        if ans == '':
            empty_answer.append(q.get('id', '?'))
        elif ans not in ['A', 'B', 'C', 'D']:
            invalid_answer.append((q.get('id', '?'), ans))
    
    print(f"\n[2] answer字段:")
    print(f"    空答案: {len(empty_answer)}道 {empty_answer[:10] if empty_answer else ''}")
    print(f"    非法答案: {len(invalid_answer)}道 {invalid_answer[:10] if invalid_answer else ''}")
    if empty_answer:
        warnings.append(f"answer为空: {len(empty_answer)}道题，id={empty_answer[:10]}")
    if invalid_answer:
        errors.append(f"answer非法(非A/B/C/D): {len(invalid_answer)}道题")
    
    # 3. 字段完整性
    required = ['id', 'bigSubject', 'smallSubject', 'year', 'question', 'A', 'B', 'C', 'D', 'answer', 'analysis']
    missing_fields = []
    for q in data:
        for field in required:
            if field not in q:
                missing_fields.append((q.get('id', '?'), field))
    
    print(f"\n[3] 字段完整性:")
    if missing_fields:
        print(f"    缺失字段: {len(missing_fields)}处")
        for mid, field in missing_fields[:10]:
            print(f"      id={mid}, 缺失={field}")
        errors.append(f"字段缺失: {len(missing_fields)}处")
    else:
        print(f"    所有题目字段完整")
    
    # 4. bigSubject检查
    invalid_big = []
    for q in data:
        bs = q.get('bigSubject', '')
        if bs not in ['公共基础', '专业基础']:
            invalid_big.append((q.get('id', '?'), bs))
    
    print(f"\n[4] bigSubject:")
    if invalid_big:
        print(f"    非法值: {len(invalid_big)}道 {invalid_big[:5]}")
        errors.append(f"bigSubject非法: {len(invalid_big)}道题")
    else:
        # 统计分布
        from collections import Counter
        bs_count = Counter(q['bigSubject'] for q in data)
        print(f"    分布: {dict(bs_count)}")
    
    # 5. id唯一性和连续性
    ids = [q['id'] for q in data]
    id_set = set(ids)
    dup_ids = [x for x in id_set if ids.count(x) > 1]
    print(f"\n[5] id检查:")
    print(f"    id范围: {min(ids)}-{max(ids)}")
    print(f"    唯一性: {'唯一' if len(ids) == len(id_set) else '有重复'}")
    if dup_ids:
        errors.append(f"id重复: {dup_ids[:10]}")
        print(f"    重复id: {dup_ids[:10]}")
    
    # 6. HTML表格和LaTeX检查
    html_table_count = 0
    latex_count = 0
    broken_html = []
    broken_latex = []
    
    for q in data:
        text = q.get('question', '') + q.get('analysis', '')
        # HTML表格
        if '<table' in text or '<tr' in text or '<td' in text:
            html_table_count += 1
            # 检查标签闭合
            if text.count('<table') != text.count('</table>'):
                broken_html.append(q.get('id', '?'))
        # LaTeX公式
        latex_matches = re.findall(r'\$[^$]+\$', text)
        if latex_matches:
            latex_count += 1
        # 检查未闭合的$
        if text.count('$') % 2 != 0:
            broken_latex.append(q.get('id', '?'))
    
    print(f"\n[6] HTML表格/LaTeX公式:")
    print(f"    含HTML表格的题: {html_table_count}道")
    print(f"    含LaTeX公式的题: {latex_count}道")
    print(f"    HTML标签未闭合: {len(broken_html)}道 {broken_html[:5] if broken_html else ''}")
    print(f"    LaTeX $未配对: {len(broken_latex)}道 {broken_latex[:5] if broken_latex else ''}")
    if broken_html:
        errors.append(f"HTML表格标签未闭合: {len(broken_html)}道题，id={broken_html[:5]}")
    if broken_latex:
        warnings.append(f"LaTeX $符号未配对: {len(broken_latex)}道题，id={broken_latex[:5]}")
    
    # 7. 空字段统计
    empty_question = sum(1 for q in data if q.get('question', '') == '')
    empty_analysis = sum(1 for q in data if q.get('analysis', '') == '')
    empty_opts = {opt: sum(1 for q in data if q.get(opt, '') == '') for opt in ['A', 'B', 'C', 'D']}
    
    print(f"\n[7] 空字段统计:")
    print(f"    空题干: {empty_question}道")
    print(f"    空解析: {empty_analysis}道")
    print(f"    空选项: {empty_opts}")
    if empty_question:
        errors.append(f"题干为空: {empty_question}道题")
    if empty_analysis:
        warnings.append(f"解析为空: {empty_analysis}道题")
    
    # 8. 年份统计
    from collections import Counter
    year_count = Counter(q['year'] for q in data)
    print(f"\n[8] 年份分布:")
    for y in sorted(year_count.keys()):
        print(f"    {y}: {year_count[y]}道")
    
    # 9. 小科目统计
    subject_count = Counter(q['smallSubject'] for q in data)
    print(f"\n[9] 小科目数量: {len(subject_count)}个")
    
    return errors, warnings

# 校验两份题库
pub_errors, pub_warnings = validate_questions(
    r'D:\应用程序开发\刷题\all_questions_final.json',
    '公共基础题库'
)

prof_errors, prof_warnings = validate_questions(
    r'D:\应用程序开发\刷题\prof_questions_final_v2.json',
    '专业基础题库'
)

# 汇总
print(f"\n{'='*60}")
print("校验汇总")
print(f"{'='*60}")
print(f"\n公共基础:")
print(f"  错误: {len(pub_errors)}项")
for e in pub_errors:
    print(f"    - {e}")
print(f"  警告: {len(pub_warnings)}项")
for w in pub_warnings:
    print(f"    - {w}")

print(f"\n专业基础:")
print(f"  错误: {len(prof_errors)}项")
for e in prof_errors:
    print(f"    - {e}")
print(f"  警告: {len(prof_warnings)}项")
for w in prof_warnings:
    print(f"    - {w}")
