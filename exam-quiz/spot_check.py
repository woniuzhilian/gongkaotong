import sys, json, random
sys.stdout.reconfigure(encoding='utf-8')

# 抽查公共基础3道题
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    pub = json.load(f)

print("="*60)
print("公共基础抽查（3道题）")
print("="*60)

# 选择不同年份的题
sample_ids = [100, 500, 1000]
for qid in sample_ids:
    q = pub[qid - 1]
    print(f"\n--- id={q['id']} ---")
    print(f"年份: {q['year']}")
    print(f"小科目: {q['smallSubject']}")
    print(f"题干: {q['question'][:100]}")
    print(f"A: {q['A'][:50]}")
    print(f"B: {q['B'][:50]}")
    print(f"C: {q['C'][:50]}")
    print(f"D: {q['D'][:50]}")
    print(f"答案: {q['answer']}")
    print(f"解析: {q['analysis'][:100]}")

# 抽查专业基础3道题
with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'r', encoding='utf-8') as f:
    prof = json.load(f)

print("\n" + "="*60)
print("专业基础抽查（3道题）")
print("="*60)

sample_ids = [50, 200, 450]
for qid in sample_ids:
    q = prof[qid - 1]
    print(f"\n--- id={q['id']} ---")
    print(f"年份: {q['year']}")
    print(f"小科目: {q['smallSubject']}")
    print(f"题干: {q['question'][:100]}")
    print(f"A: {q['A'][:50]}")
    print(f"B: {q['B'][:50]}")
    print(f"C: {q['C'][:50]}")
    print(f"D: {q['D'][:50]}")
    print(f"答案: {q['answer']}")
    print(f"解析: {q['analysis'][:100]}")

# 检查公共基础空选项
print("\n" + "="*60)
print("公共基础空选项检查")
print("="*60)
empty_opt_questions = []
for q in pub:
    empty_opts = [opt for opt in ['A', 'B', 'C', 'D'] if q[opt] == '']
    if empty_opts:
        empty_opt_questions.append((q['id'], q['year'], empty_opts, q['question'][:50]))

print(f"共{len(empty_opt_questions)}道题有空选项")
for qid, year, opts, q in empty_opt_questions[:10]:
    print(f"  id={qid}, {year}, 空选项={opts}, 题干={q}")
