import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 题干中明确引用图片的关键词
img_keywords = ['如图', '图所示', '图中', '下图', '上图', '图示', '见图', '图为', '图是']

img_questions = []
for q in data:
    qtext = q['question']
    # 检查题干是否包含图片引用关键词
    has_img_ref = any(kw in qtext for kw in img_keywords)
    if has_img_ref:
        # 提取页码
        m = re.search(r'PDF第(\d+)页', qtext)
        page = m.group(1) if m else '?'
        # 提取题干（去掉配图标记）
        qclean = re.sub(r'【本题配图，PDF第\d+页】', '', qtext).strip()
        # 截断题干
        qshort = qclean[:55] + ('...' if len(qclean) > 55 else '')
        img_questions.append({
            'id': q['id'],
            'year': q['year'],
            'smallSubject': q['smallSubject'],
            'page': page,
            'question': qshort
        })

print(f"共 {len(img_questions)} 道题干明确引用图片的题目\n")
print(f"{'id':<6}{'年份':<8}{'PDF页':<8}{'小科目':<22}题干摘要")
print("-" * 100)
for q in img_questions:
    print(f"{q['id']:<6}{q['year']:<8}{q['page']:<8}{q['smallSubject']:<22}{q['question']}")
