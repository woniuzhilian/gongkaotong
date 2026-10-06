import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

q_pattern = re.compile(r'【\s*(\d{4})\s*(补)?\s*-\s*(\d+)\s*】')

print("="*70)
print("专业基础题目缺失清单（按年份）")
print("="*70)

with open(r'D:\应用程序开发\刷题\prof_questions_raw.txt', 'r', encoding='utf-8') as f:
    raw = f.read()

all_marks = q_pattern.findall(raw)
year_nums = {}
for year, bu, num in all_marks:
    y = year + ('补' if bu else '')
    if y not in year_nums:
        year_nums[y] = set()
    year_nums[y].add(int(num))

expected = set(range(1, 61))
total_missing = 0
missing_detail = []

for y in sorted(year_nums.keys()):
    nums = year_nums[y]
    missing = sorted(expected - nums)
    extra = sorted(nums - expected)
    total_missing += len(missing)
    print(f"\n{y}年: 应有60题, 实有{len(nums)}题, 缺失{len(missing)}题")
    if missing:
        print(f"  缺失题号: {missing}")
        for m in missing:
            missing_detail.append(f"{y}-{m}")
    if extra:
        print(f"  超出范围: {extra}")

print(f"\n{'='*70}")
print(f"专业基础总计缺失: {total_missing}题")
print(f"OCR识别到: {sum(len(v) for v in year_nums.values())}题")
print(f"理论应有: {len(year_nums)*60}题 ({len(year_nums)}个年份×60题)")
print(f"{'='*70}")

print("\n缺失题目完整清单:")
for i, item in enumerate(missing_detail, 1):
    print(f"  {i}. {item}", end="")
    if i % 10 == 0:
        print()
print()

# 公共基础核查
print("\n" + "="*70)
print("公共基础题目缺失清单（按年份）")
print("="*70)

with open(r'D:\应用程序开发\刷题\questions_raw.txt', 'r', encoding='utf-8') as f:
    raw1 = f.read()

all_marks1 = q_pattern.findall(raw1)
year_nums1 = {}
for year, bu, num in all_marks1:
    y = year + ('补' if bu else '')
    if y not in year_nums1:
        year_nums1[y] = set()
    year_nums1[y].add(int(num))

expected1 = set(range(1, 121))
total_missing1 = 0
missing_detail1 = []

for y in sorted(year_nums1.keys()):
    nums = year_nums1[y]
    missing = sorted(expected1 - nums)
    total_missing1 += len(missing)
    if missing:
        print(f"\n{y}年: 应有120题, 实有{len(nums)}题, 缺失{len(missing)}题")
        print(f"  缺失题号: {missing}")
        for m in missing:
            missing_detail1.append(f"{y}-{m}")
    else:
        print(f"{y}年: 120题齐全")

# 2016-66重复
print(f"\n注意: 2016-66在PDF中出现2次（重复），JSON中保留1道")

print(f"\n公共基础总计缺失: {total_missing1}题")
print(f"缺失题目: {missing_detail1}")
