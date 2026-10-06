import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 检查id=150-155附近的题目
print("=== JSON中id=150-155的题目 ===")
for q in data:
    if 150 <= q['id'] <= 155:
        qclean = re.sub(r'【本题配图，PDF第\d+页】', '', q['question']).strip()
        print(f"id={q['id']}, year={q['year']}, smallSubject={q['smallSubject']}")
        print(f"  题干: {qclean[:70]}")
        print()

# 统计2021年积分学的题目数量
print("=== 2021年积分学题目 ===")
count = 0
for q in data:
    if q['year'] == '2021' and q['smallSubject'] == '积分学':
        count += 1
        qclean = re.sub(r'【本题配图，PDF第\d+页】', '', q['question']).strip()
        print(f"id={q['id']}: {qclean[:60]}")
print(f"共{count}道")

# 检查PDF中2021年积分学有多少道题
with open(r'D:\应用程序开发\刷题\questions_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 找2021年积分学章节的题目
# 先找积分学章节的位置
print("\n=== PDF中2021年积分学相关标记 ===")
# 找所有2021年的标记
pattern = re.compile(r'【\s*(\d{4}\s*补?)\s*-\s*(\d+)\s*】')
matches = list(pattern.finditer(text))
count_2021 = 0
for m in matches:
    year = m.group(1).replace(' ', '')
    qnum = m.group(2)
    if year == '2021':
        count_2021 += 1
        # 看上下文判断是否积分学
        start = m.end()
        end = min(len(text), start + 100)
        context = text[start:end].replace('\n', ' ')
        if count_2021 <= 20:  # 积分学应该在前20道左右
            print(f"  2021-{qnum}: {context[:60]}")
print(f"PDF中2021年题目共{count_2021}道")
