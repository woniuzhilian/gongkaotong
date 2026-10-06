import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 搜索"设函数f(u)连续"这道题（2021-14）
for q in data:
    if '设函数' in q['question'] and '连续' in q['question'] and '区域' in q['question']:
        qclean = re.sub(r'【本题配图，PDF第\d+页】', '', q['question']).strip()
        print(f"找到: id={q['id']}, year={q['year']}, smallSubject={q['smallSubject']}")
        print(f"  题干: {qclean[:100]}")
        print()

# 统计2019年气体动理论的题目数量
count = 0
for q in data:
    if q['year'] == '2019' and q['smallSubject'] == '气体动理论与热力学基础':
        count += 1
        qclean = re.sub(r'【本题配图，PDF第\d+页】', '', q['question']).strip()
        print(f"id={q['id']}: {qclean[:60]}")
print(f"\n2019年气体动理论题目共{count}道")
