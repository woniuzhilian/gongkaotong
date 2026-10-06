import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(r'D:\应用程序开发\刷题\prof2_merged.json', 'r', encoding='utf-8') as f:
    new_data = json.load(f)

with open(r'D:\应用程序开发\刷题\prof_merged_full.json', 'r', encoding='utf-8') as f:
    full_data = json.load(f)

# 建立id到_qnum的映射
id_to_qnum = {}
for q in full_data:
    id_to_qnum[q['id']] = (q['year'], q['_qnum'])

# 检查选项为空的题目，在新题库中是否有正确内容
print("=== 检查选项为空的题目（2016-2023年）===")
fix_count = 0
for q in data:
    empty_opts = [opt for opt in ['A', 'B', 'C', 'D'] if q[opt] == '']
    if not empty_opts:
        continue
    
    year, qnum = id_to_qnum.get(q['id'], (None, None))
    if year is None or year == '2024':
        continue
    
    # 在新题库中查找
    if year in new_data and str(qnum) in new_data[year]:
        new_q = new_data[year][str(qnum)]
        new_empty = [opt for opt in ['A', 'B', 'C', 'D'] if new_q[opt] == '']
        
        if len(new_empty) < len(empty_opts):
            # 新题库有更多选项内容，可以修正
            print(f"id={q['id']}, {year}年第{qnum}题: 原空={empty_opts}, 新空={new_empty}")
            print(f"  原题干: {q['question'][:50]}")
            print(f"  新题干: {new_q['question'][:50]}")
            for opt in ['A', 'B', 'C', 'D']:
                if q[opt] == '' and new_q[opt] != '':
                    print(f"  {opt}: 新值={new_q[opt][:40]}")
            fix_count += 1

print(f"\n可修正题目数: {fix_count}")
