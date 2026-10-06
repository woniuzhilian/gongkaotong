import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

# 加载新题库（完整年份版）
with open(r'D:\应用程序开发\刷题\prof2_merged.json', 'r', encoding='utf-8') as f:
    new_data = json.load(f)

# 加载现有题库（分类版）
with open(r'D:\应用程序开发\刷题\prof_questions_final.json', 'r', encoding='utf-8') as f:
    old_data = json.load(f)

# 建立现有题库的年份-题号 -> 小科目映射
old_subject_map = {}
for q in old_data:
    key = f"{q['year']}-{q.get('_qnum', '')}"
    # 现有题库没有_qnum了，需要从question推断
    # 实际上我们需要重新加载带_qnum的版本
    pass

# 重新加载带内部字段的版本
with open(r'D:\应用程序开发\刷题\prof_all_questions.json', 'r', encoding='utf-8') as f:
    old_full = json.load(f)

old_subject_map = {}
old_question_map = {}
for q in old_full:
    key = f"{q['year']}-{q['_qnum']}"
    old_subject_map[key] = q['smallSubject']
    old_question_map[key] = q

# 题号到小科目的大致映射（用于匹配不到的情况）
def get_subject_by_qnum(qnum):
    n = int(qnum)
    if n <= 12:
        return '土木工程材料'
    elif n <= 20:
        return '工程测量'
    elif n <= 30:
        return '土木工程施工与管理'
    elif n <= 40:
        return '结构力学'
    elif n <= 50:
        return '土力学与地基基础'
    else:
        return '工程地质'

# 合并题库
merged_questions = []
big_subject = '专业基础'

# 年份顺序
years_order = ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '2022补', '2023', '2024']

for year in years_order:
    if year == '2024':
        # 2024年从现有题库获取
        year_questions = [q for q in old_full if q['year'] == '2024']
        for q in year_questions:
            merged_questions.append({
                'bigSubject': big_subject,
                'smallSubject': q['smallSubject'],
                'year': q['year'],
                'question': q['question'],
                'A': q['A'],
                'B': q['B'],
                'C': q['C'],
                'D': q['D'],
                'answer': q['answer'],
                'analysis': q['analysis'],
                '_qnum': int(q['_qnum'])
            })
    elif year in new_data:
        year_data = new_data[year]
        for qnum_str in sorted(year_data.keys(), key=int):
            qnum = int(qnum_str)
            q = year_data[qnum_str]
            key = f"{year}-{qnum}"

            # 确定小科目
            if key in old_subject_map:
                small_subject = old_subject_map[key]
            else:
                small_subject = get_subject_by_qnum(qnum)

            merged_questions.append({
                'bigSubject': big_subject,
                'smallSubject': small_subject,
                'year': year,
                'question': q['question'],
                'A': q['A'],
                'B': q['B'],
                'C': q['C'],
                'D': q['D'],
                'answer': q['answer'],
                'analysis': q['analysis'],
                '_qnum': qnum
            })

        # 补充新题库中缺失的题目（从现有题库，只补充缺失的题号）
        existing_nums = set(int(k) for k in year_data.keys())
        for q in old_full:
            if q['year'] == year:
                qnum = int(q['_qnum'])
                if qnum not in existing_nums:
                    merged_questions.append({
                        'bigSubject': big_subject,
                        'smallSubject': q['smallSubject'],
                        'year': q['year'],
                        'question': q['question'],
                        'A': q['A'],
                        'B': q['B'],
                        'C': q['C'],
                        'D': q['D'],
                        'answer': q['answer'],
                        'analysis': q['analysis'],
                        '_qnum': qnum
                    })
                    existing_nums.add(qnum)

# 按年份和题号排序
def sort_key(q):
    year_order = years_order.index(q['year']) if q['year'] in years_order else 99
    return (year_order, int(q['_qnum']))

merged_questions.sort(key=sort_key)

# 重新编号id
for i, q in enumerate(merged_questions, 1):
    q['id'] = i

# 统计
print(f"合并后总题数: {len(merged_questions)}")
year_counts = {}
for q in merged_questions:
    year_counts[q['year']] = year_counts.get(q['year'], 0) + 1
print("\n按年份统计:")
for year in years_order:
    print(f"  {year}: {year_counts.get(year, 0)}道")

# 检查缺失
print("\n各年份缺失题号:")
for year in years_order:
    if year == '2024':
        expected = 60
    else:
        expected = 60
    nums = set(q['_qnum'] for q in merged_questions if q['year'] == year)
    missing = [i for i in range(1, expected+1) if i not in nums]
    if missing:
        print(f"  {year}: 缺失{missing}")
    else:
        print(f"  {year}: 齐全")

# 保存（带内部字段）
with open(r'D:\应用程序开发\刷题\prof_merged_full.json', 'w', encoding='utf-8') as f:
    json.dump(merged_questions, f, ensure_ascii=False, indent=2)

# 保存最终版本（去掉内部字段）
final_data = []
for q in merged_questions:
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

print(f"\n已保存 prof_questions_final_v2.json ({len(final_data)}题)")
