import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("详细问题检查")
print("="*60)

# 公共基础
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data1 = json.load(f)

print("\n【公共基础】选项为空的题目:")
empty_opts1 = []
for q in data1:
    for opt in ['A', 'B', 'C', 'D']:
        if not q.get(opt, '').strip():
            empty_opts1.append((q['id'], q['year'], q['_qnum'] if '_qnum' in q else '', opt, q['smallSubject']))
print(f"  共{len(empty_opts1)}个空选项")
for item in empty_opts1[:15]:
    print(f"  id={item[0]}, {item[1]}-{item[2]}, 选项{item[3]}为空, 科目:{item[4]}")
if len(empty_opts1) > 15:
    print(f"  ...还有{len(empty_opts1)-15}个")

# 专业基础
with open(r'D:\应用程序开发\刷题\prof_questions_final.json', 'r', encoding='utf-8') as f:
    data2 = json.load(f)

print("\n【专业基础】解析为空的题目:")
empty_ana2 = []
for q in data2:
    if not q.get('analysis', '').strip():
        empty_ana2.append((q['id'], q['year'], q['smallSubject'], q['question'][:50]))
print(f"  共{len(empty_ana2)}道")
for item in empty_ana2:
    print(f"  id={item[0]}, {item[1]}, {item[2]}: {item[3]}")

print("\n【专业基础】选项为空的题目:")
empty_opts2 = []
for q in data2:
    for opt in ['A', 'B', 'C', 'D']:
        if not q.get(opt, '').strip():
            empty_opts2.append((q['id'], q['year'], opt, q['smallSubject'], q['question'][:40]))
print(f"  共{len(empty_opts2)}个空选项")
for item in empty_opts2:
    print(f"  id={item[0]}, {item[1]}, 选项{item[2]}为空, {item[3]}: {item[4]}")

# 检查answer为空的题目
print("\n【公共基础】answer为空的题目:")
empty_ans1 = [q for q in data1 if not q.get('answer', '')]
print(f"  共{len(empty_ans1)}道")
for q in empty_ans1[:5]:
    print(f"  id={q['id']}, {q['year']}, {q['smallSubject']}")

print("\n【专业基础】answer为空的题目:")
empty_ans2 = [q for q in data2 if not q.get('answer', '')]
print(f"  共{len(empty_ans2)}道")
for q in empty_ans2:
    print(f"  id={q['id']}, {q['year']}, {q['smallSubject']}: {q['question'][:50]}")

# 检查OCR残留符号
print("\n【专业基础】解析含OCR残留符号的题目:")
ocr_residual = []
for q in data2:
    ana = q.get('analysis', '')
    if ana.startswith('】') or ana.startswith('【') or '】' in ana[:5]:
        ocr_residual.append(q['id'])
print(f"  共{len(ocr_residual)}道，示例id: {ocr_residual[:10]}")

# 检查年份格式
print("\n【年份格式检查】")
years1 = set(q['year'] for q in data1)
years2 = set(q['year'] for q in data2)
print(f"  公共基础年份: {sorted(years1)}")
print(f"  专业基础年份: {sorted(years2)}")
