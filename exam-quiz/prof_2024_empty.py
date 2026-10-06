import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_merged_full.json', 'r', encoding='utf-8') as f:
    full_data = json.load(f)

# 找出2024年选项为空的题目
print("=== 2024年选项为空的题目 ===")
for q in full_data:
    if q['year'] == '2024':
        empty_opts = [opt for opt in ['A', 'B', 'C', 'D'] if q[opt] == '']
        if empty_opts:
            print(f"id={q['id']}, qnum={q['_qnum']}, 小科目={q['smallSubject']}, 空选项={empty_opts}")
            print(f"  题干: {q['question'][:80]}")
            print()
