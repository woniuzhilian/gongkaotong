import sys, json
sys.stdout.reconfigure(encoding='utf-8')
with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

empty_opt_count = 0
for q in data:
    for opt in ['A', 'B', 'C', 'D']:
        if q[opt] == '':
            empty_opt_count += 1
            print(f"id={q['id']}, {q['year']}, 空选项={opt}")

print(f"\n空选项总数: {empty_opt_count}")
print(f"总题数: {len(data)}")

img_opt_count = 0
for q in data:
    for opt in ['A', 'B', 'C', 'D']:
        if '选项配图' in q[opt]:
            img_opt_count += 1
print(f"含配图标记的选项: {img_opt_count}个")
