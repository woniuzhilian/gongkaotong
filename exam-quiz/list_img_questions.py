import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

img_questions = []
for q in data:
    if '【本题配图' in q['question']:
        # 提取页码
        m = re.search(r'PDF第(\d+)页', q['question'])
        page = m.group(1) if m else '?'
        # 提取题干（去掉配图标记）
        qtext = re.sub(r'【本题配图，PDF第\d+页】', '', q['question']).strip()
        # 截断题干
        qshort = qtext[:50] + ('...' if len(qtext) > 50 else '')
        img_questions.append({
            'id': q['id'],
            'year': q['year'],
            'smallSubject': q['smallSubject'],
            'page': page,
            'question': qshort
        })

print(f"共 {len(img_questions)} 道含插图的题目\n")
print(f"{'id':<6}{'年份':<8}{'PDF页':<8}{'小科目':<20}题干摘要")
print("-" * 90)
for q in img_questions:
    print(f"{q['id']:<6}{q['year']:<8}{q['page']:<8}{q['smallSubject']:<20}{q['question']}")
