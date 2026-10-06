import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"总题数: {len(data)}")

# 1. JSON语法 - 已加载成功
print("\n1. JSON语法: 合法")

# 2. answer字段检查
invalid_answer = [q['id'] for q in data if q['answer'] not in ['A', 'B', 'C', 'D', '']]
empty_answer = [q['id'] for q in data if q['answer'] == '']
print(f"\n2. answer字段: 非法={len(invalid_answer)}, 为空={len(empty_answer)}")
if empty_answer:
    print(f"   空答案题号id: {empty_answer[:10]}")

# 3. 字段完整性
required = ['id', 'bigSubject', 'smallSubject', 'year', 'question', 'A', 'B', 'C', 'D', 'answer', 'analysis']
missing_fields = []
for q in data:
    for f in required:
        if f not in q:
            missing_fields.append((q['id'], f))
print(f"\n3. 字段完整性: 缺失={len(missing_fields)}")

# 4. bigSubject检查
invalid_big = [q['id'] for q in data if q['bigSubject'] not in ['公共基础', '专业基础']]
print(f"\n4. bigSubject: 非法={len(invalid_big)}")

# 5. 小科目统计
subjects = {}
for q in data:
    s = q['smallSubject']
    subjects[s] = subjects.get(s, 0) + 1
print(f"\n5. 小科目分布:")
for s, c in sorted(subjects.items(), key=lambda x: -x[1]):
    print(f"   {s}: {c}道")

# 6. 年份统计
years = {}
for q in data:
    y = q['year']
    years[y] = years.get(y, 0) + 1
print(f"\n6. 年份分布:")
for y in sorted(years.keys()):
    print(f"   {y}: {years[y]}道")

# 7. OCR残留符号检查
bracket_count = sum(1 for q in data if q['analysis'].startswith('】') or q['analysis'].startswith('】'))
print(f"\n7. 解析开头有】残留: {bracket_count}道")

# 8. 空选项统计
empty_opts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
for q in data:
    for opt in ['A', 'B', 'C', 'D']:
        if q[opt] == '':
            empty_opts[opt] += 1
print(f"\n8. 空选项: {empty_opts}")

# 9. 空解析统计
empty_analysis = sum(1 for q in data if q['analysis'] == '')
print(f"\n9. 空解析: {empty_analysis}道")

# 10. id唯一性
ids = [q['id'] for q in data]
print(f"\n10. id唯一性: {'唯一' if len(ids) == len(set(ids)) else '有重复'}")
print(f"    id范围: {min(ids)}-{max(ids)}")
