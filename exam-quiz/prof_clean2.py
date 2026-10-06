import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. 清理解析开头的】残留
cleaned_count = 0
for q in data:
    if q['analysis'].startswith('】') or q['analysis'].startswith('】'):
        q['analysis'] = q['analysis'][1:].strip()
        cleaned_count += 1
    # 清理开头可能的其他OCR残留
    q['analysis'] = re.sub(r'^[】\]\}>\s]+', '', q['analysis'])

print(f"清理了解析开头残留: {cleaned_count}道")

# 2. 检查id=20的答案
q20 = [q for q in data if q['id'] == 20][0]
print(f"\nid=20题目:")
print(f"  年份: {q20['year']}, 小科目: {q20['smallSubject']}")
print(f"  题干: {q20['question'][:80]}")
print(f"  答案: '{q20['answer']}'")
print(f"  解析: {q20['analysis'][:80]}")

# 3. 检查空答案的题目
empty_ans = [q for q in data if q['answer'] == '']
print(f"\n空答案题目数: {len(empty_ans)}")
for q in empty_ans:
    print(f"  id={q['id']}, year={q['year']}, q={q['question'][:60]}")

# 保存
with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n已保存清理后的版本")
