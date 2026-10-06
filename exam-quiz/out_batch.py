import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
start = int(sys.argv[1])
end = int(sys.argv[2])
subset = [q for q in data if start <= q['id'] <= end]
print(json.dumps(subset, ensure_ascii=False, separators=(',', ':')))
