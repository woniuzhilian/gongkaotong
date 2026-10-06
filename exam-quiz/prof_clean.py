import sys, json
sys.stdout.reconfigure(encoding='utf-8')

# 加载合并后的专业基础
with open(r'D:\应用程序开发\刷题\prof_merged_full.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 删除题号>60的无效题
cleaned = [q for q in data if int(q['_qnum']) <= 60]
removed = len(data) - len(cleaned)
print(f"删除了{removed}道题号>60的无效题")

# 重新排序和编号
years_order = ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '2022补', '2023', '2024']
cleaned.sort(key=lambda q: (years_order.index(q['year']) if q['year'] in years_order else 99, int(q['_qnum'])))

for i, q in enumerate(cleaned, 1):
    q['id'] = i

# 统计
year_counts = {}
for q in cleaned:
    year_counts[q['year']] = year_counts.get(q['year'], 0) + 1
print(f"\n清理后总题数: {len(cleaned)}")
for year in years_order:
    print(f"  {year}: {year_counts.get(year, 0)}道")

# 保存带内部字段
with open(r'D:\应用程序开发\刷题\prof_merged_full.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

# 保存最终版本
final_data = []
for q in cleaned:
    final_data.append({
        'id': q['id'],
        'bigSubject': q['bigSubject'],
        'smallSubject': q['smallSubject'],
        'year': q['year'],
        'question': q['question'],
        'A': q['A'],
        'B': q['B'],
        'C': q['C'],
        'D': q['D'],
        'answer': q['answer'],
        'analysis': q['analysis']
    })

with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print(f"\n已保存最终版本: {len(final_data)}题")
