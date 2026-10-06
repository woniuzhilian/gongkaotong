import sys, re
sys.stdout.reconfigure(encoding='utf-8')

# 检查答案PDF中是否有2021-14
with open(r'D:\应用程序开发\刷题\answers_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 找2021-14
pattern = re.compile(r'【\s*(\d{4}\s*补?)\s*-\s*(\d+)\s*】')
matches = list(pattern.finditer(text))

for m in matches:
    year = m.group(1).replace(' ', '')
    qnum = m.group(2)
    if year == '2021' and qnum == '14':
        start = m.start()
        end = min(len(text), start + 500)
        context = text[start:end]
        print(f"找到答案PDF中的2021-14:")
        print(context)
        print()
        break

# 同时检查题目PDF中2021-14的完整内容
with open(r'D:\应用程序开发\刷题\questions_raw.txt', 'r', encoding='utf-8') as f:
    qtext = f.read()

matches_q = list(pattern.finditer(qtext))
for m in matches_q:
    year = m.group(1).replace(' ', '')
    qnum = m.group(2)
    if year == '2021' and qnum == '14':
        start = m.start()
        end = min(len(qtext), start + 500)
        context = qtext[start:end]
        print(f"找到题目PDF中的2021-14:")
        print(context)
        break
