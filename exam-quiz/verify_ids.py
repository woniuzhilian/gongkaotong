import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 检查id=310-313的内容
for q in data:
    if q['id'] in [310, 311, 312, 313]:
        qclean = re.sub(r'【本题配图，PDF第\d+页】', '', q['question']).strip()
        print(f"id={q['id']}, year={q['year']}, smallSubject={q['smallSubject']}")
        print(f"  题干: {qclean[:80]}")
        print(f"  answer={q['answer']}")
        print()
