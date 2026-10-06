import sys, json
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8'))
batch = [q for q in data if 201 <= q['id'] <= 300]
print(json.dumps(batch, ensure_ascii=False, separators=(',', ':')))
