import sys, json
sys.stdout.reconfigure(encoding='utf-8')

# 加载公共基础题库
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    pub_data = json.load(f)

print(f"补全前: {len(pub_data)}道题")

# 2017-56题
q_2017_56 = {
    'bigSubject': '公共基础',
    'smallSubject': '理论力学',
    'year': '2017',
    'question': '已知动点的运动方程为 x=rcosωt，y=rsinωt，z=ut，r、u、ω 为常数，试求动点的加速度（ ）。',
    'A': 'a=rω²',
    'B': 'a=0',
    'C': 'a=r² ω',
    'D': 'a = √(rω² + u²)',
    'answer': 'A',
    'analysis': '由公式a = √(a_x² + a_y² + a_z²) = √(x\'\'² + y\'\'² + z\'\'²) = rω²。'
}

# 2018-64题
q_2018_64 = {
    'bigSubject': '公共基础',
    'smallSubject': '材料力学',
    'year': '2018',
    'question': '图示圆轴的抗扭截面系数为 W_T，切变模量为 G。扭转变形后，圆轴表面 A 点处截取的单元体互相垂直的相邻边线改变了 γ 角，如图所示。圆轴承受的扭矩是（ ）。【本题配图，PDF第11页】',
    'A': 'T=GγW_T',
    'B': 'T = Gγ/W_T',
    'C': 'T = γ/G W_T',
    'D': 'T = W_T/(Gγ)',
    'answer': 'A',
    'analysis': '根据剪应力计算公式τ = T/W_T，可得T = τW_T，又由剪切胡克定律τ=Gγ，即T = GγW_T。'
}

# 添加到题库
pub_data.append(q_2017_56)
pub_data.append(q_2018_64)

# 按年份和题号排序
# 需要从question中提取题号，或者按year排序后保持原有顺序
# 公共基础题库是按年份排序的，每年120题
# 2017年有119题（缺56），2018年有119题（缺64）
# 我们需要把新题插入到正确位置

# 先按年份分组
year_groups = {}
for q in pub_data:
    year = q['year']
    if year not in year_groups:
        year_groups[year] = []
    year_groups[year].append(q)

# 对每年的题目，尝试从question中提取题号排序
import re
def extract_qnum(question):
    # 尝试匹配题号模式
    m = re.search(r'^(\d{1,3})[、.．]', question)
    if m:
        return int(m.group(1))
    return 999

for year in year_groups:
    year_groups[year].sort(key=lambda q: extract_qnum(q['question']))

# 重新组合
years_order = ['2013', '2014', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2022补', '2023', '2024']
sorted_data = []
for year in years_order:
    if year in year_groups:
        sorted_data.extend(year_groups[year])

# 重新编号
for i, q in enumerate(sorted_data, 1):
    q['id'] = i

print(f"补全后: {len(sorted_data)}道题")

# 统计各年份
year_counts = {}
for q in sorted_data:
    year_counts[q['year']] = year_counts.get(q['year'], 0) + 1
print("\n各年份题数:")
for year in years_order:
    print(f"  {year}: {year_counts.get(year, 0)}道")

# 保存
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_data, f, ensure_ascii=False, indent=2)

print(f"\n已保存 all_questions_final.json ({len(sorted_data)}题)")
