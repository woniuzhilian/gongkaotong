import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. 找出解析为空的题目
print("=== 解析为空的题目 ===")
empty_analysis = []
for q in data:
    if q['analysis'] == '':
        empty_analysis.append(q)
        print(f"id={q['id']}, {q['year']}年第{q.get('_qnum', '?')}题, 小科目={q['smallSubject']}")
        print(f"  题干: {q['question'][:80]}")
        print(f"  A={q['A'][:30]}, B={q['B'][:30]}, C={q['C'][:30]}, D={q['D'][:30]}")
        print(f"  答案: {q['answer']}")
        print()

print(f"共{len(empty_analysis)}道题解析为空")

# 2. 找出选项为空的题目（可能是图形选项）
print("\n=== 选项为空的题目 ===")
empty_opt_questions = []
for q in data:
    empty_opts = [opt for opt in ['A', 'B', 'C', 'D'] if q[opt] == '']
    if empty_opts:
        empty_opt_questions.append((q, empty_opts))
        print(f"id={q['id']}, {q['year']}年, 空选项={empty_opts}")
        print(f"  题干: {q['question'][:60]}")

print(f"\n共{len(empty_opt_questions)}道题有选项为空")
