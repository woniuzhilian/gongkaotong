import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

q_pattern = re.compile(r'【\s*(\d{4})\s*(补)?\s*-\s*(\d+)\s*】')

print("="*60)
print("公共基础题目数量核查")
print("="*60)

with open(r'D:\应用程序开发\刷题\questions_raw.txt', 'r', encoding='utf-8') as f:
    raw1 = f.read()

# 提取所有题目标记
all_marks1 = q_pattern.findall(raw1)
print(f"原始PDF中题目标记总数: {len(all_marks1)}")

# 按年份统计
year_counts1 = {}
year_nums1 = {}
for year, bu, num in all_marks1:
    y = year + ('补' if bu else '')
    if y not in year_counts1:
        year_counts1[y] = 0
        year_nums1[y] = set()
    year_counts1[y] += 1
    year_nums1[y].add(int(num))

print(f"\n按年份统计（原始标记）:")
for y in sorted(year_counts1.keys()):
    nums = sorted(year_nums1[y])
    expected = set(range(1, 121))
    missing = expected - set(nums)
    dup_count = year_counts1[y] - len(nums)
    print(f"  {y}: {year_counts1[y]}个标记, {len(nums)}个不重复题号, 缺失{len(missing)}题, 重复{dup_count}个")
    if missing:
        print(f"    缺失题号: {sorted(missing)}")

# 检查重复
print(f"\n重复题目标记:")
from collections import Counter
mark_counter = Counter([f"{y}{'补' if bu else ''}-{n}" for y, bu, n in all_marks1])
for mark, count in mark_counter.items():
    if count > 1:
        print(f"  {mark}: 出现{count}次")

print("\n" + "="*60)
print("专业基础题目数量核查")
print("="*60)

with open(r'D:\应用程序开发\刷题\prof_questions_raw.txt', 'r', encoding='utf-8') as f:
    raw2 = f.read()

all_marks2 = q_pattern.findall(raw2)
print(f"OCR文本中题目标记总数: {len(all_marks2)}")

year_counts2 = {}
year_nums2 = {}
for year, bu, num in all_marks2:
    y = year + ('补' if bu else '')
    if y not in year_counts2:
        year_counts2[y] = 0
        year_nums2[y] = set()
    year_counts2[y] += 1
    year_nums2[y].add(int(num))

print(f"\n按年份统计（OCR标记）:")
for y in sorted(year_counts2.keys()):
    nums = sorted(year_nums2[y])
    expected = set(range(1, 61))
    missing = expected - set(nums)
    dup_count = year_counts2[y] - len(nums)
    print(f"  {y}: {year_counts2[y]}个标记, {len(nums)}个不重复题号, 缺失{len(missing)}题, 重复{dup_count}个")
    if missing:
        print(f"    缺失题号: {sorted(missing)}")

# 检查重复
print(f"\n重复题目标记:")
mark_counter2 = Counter([f"{y}{'补' if bu else ''}-{n}" for y, bu, n in all_marks2])
for mark, count in mark_counter2.items():
    if count > 1:
        print(f"  {mark}: 出现{count}次")

# 对比JSON中的题目数
print("\n" + "="*60)
print("JSON中题目数量")
print("="*60)

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data1 = json.load(f)
json_years1 = {}
for q in data1:
    y = q['year']
    json_years1[y] = json_years1.get(y, 0) + 1
print(f"\n公共基础JSON: {len(data1)}道")
for y in sorted(json_years1.keys()):
    print(f"  {y}: {json_years1[y]}道")

with open(r'D:\应用程序开发\刷题\prof_questions_final.json', 'r', encoding='utf-8') as f:
    data2 = json.load(f)
json_years2 = {}
for q in data2:
    y = q['year']
    json_years2[y] = json_years2.get(y, 0) + 1
print(f"\n专业基础JSON: {len(data2)}道")
for y in sorted(json_years2.keys()):
    print(f"  {y}: {json_years2[y]}道")
