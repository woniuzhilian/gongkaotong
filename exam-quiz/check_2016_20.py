import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof2_merged.json', 'r', encoding='utf-8') as f:
    new_data = json.load(f)

# 查找2016年第20题
if '2016' in new_data and '20' in new_data['2016']:
    q = new_data['2016']['20']
    print(f"2016年第20题:")
    print(f"  题干: {q['question'][:100]}")
    print(f"  A: {q['A']}")
    print(f"  B: {q['B']}")
    print(f"  C: {q['C']}")
    print(f"  D: {q['D']}")
    print(f"  答案: {q['answer']}")
    print(f"  解析: {q['analysis'][:100]}")
else:
    print("2016年第20题不存在于新题库中")
    # 列出2016年所有题号
    if '2016' in new_data:
        print(f"2016年题号: {sorted(new_data['2016'].keys(), key=int)}")
