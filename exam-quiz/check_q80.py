import sys, json
sys.stdout.reconfigure(encoding='utf-8')
with open(r'D:\应用程序开发\刷题\prof_merged_full.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for q in data:
    if q['year'] == '2021' and str(q['_qnum']) == '80':
        print(f"id={q['id']}, qnum={q['_qnum']}")
        print(f"题干: {q['question'][:150]}")
        print(f"A: {q['A'][:60]}")
        print(f"B: {q['B'][:60]}")
        print(f"答案: {q['answer']}")
        print(f"小科目: {q['smallSubject']}")
