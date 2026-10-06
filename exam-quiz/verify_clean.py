import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 检查之前有问题的几道题
for qid in [706, 1344, 1440]:
    q = data[qid - 1]
    print(f"id={qid}:")
    print(f"  D选项: {q['D']}")
    print()
