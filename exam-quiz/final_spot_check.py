import sys, json
sys.stdout.reconfigure(encoding='utf-8')

# 抽查公共基础3道题
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    pub = json.load(f)

print("="*60)
print("公共基础抽查（3道题）")
print("="*60)

for qid in [1, 720, 1440]:
    q = pub[qid - 1]
    print(f"\n--- id={q['id']} ---")
    print(f"年份: {q['year']}")
    print(f"小科目: {q['smallSubject']}")
    print(f"题干: {q['question'][:80]}")
    print(f"A: {q['A'][:40]}")
    print(f"B: {q['B'][:40]}")
    print(f"C: {q['C'][:40]}")
    print(f"D: {q['D'][:40]}")
    print(f"答案: {q['answer']}")
    print(f"解析: {q['analysis'][:80]}")

# 抽查专业基础3道题（OCR清理后）
with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'r', encoding='utf-8') as f:
    prof = json.load(f)

print("\n" + "="*60)
print("专业基础抽查（3道题，OCR清理后）")
print("="*60)

for qid in [9, 50, 450]:
    q = prof[qid - 1]
    print(f"\n--- id={q['id']} ---")
    print(f"年份: {q['year']}")
    print(f"小科目: {q['smallSubject']}")
    print(f"题干: {q['question'][:80]}")
    print(f"A: {q['A'][:40]}")
    print(f"B: {q['B'][:40]}")
    print(f"C: {q['C'][:40]}")
    print(f"D: {q['D'][:40]}")
    print(f"答案: {q['answer']}")
    print(f"解析: {q['analysis'][:80]}")
