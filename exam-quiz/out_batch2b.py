import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
subset = [q for q in data if 301 <= q['id'] <= 400]
print(json.dumps(subset, ensure_ascii=False, separators=(',', ':')))
