import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    pub = json.load(f)

failed_ids = [9, 250, 252, 569, 721]
for qid in failed_ids:
    q = pub[qid - 1]
    print(f"id={qid}, year={q['year']}")
    print(f"  题干: {q['question'][:150]}")
    print(f"  A: {q['A'][:50]}")
    print(f"  B: {q['B'][:50]}")
    print(f"  C: {q['C'][:50]}")
    print(f"  D: {q['D'][:50]}")
    print()
