import json, sys, re, os
sys.stdout.reconfigure(encoding='utf-8')

# 加载已有映射
with open(r'D:\应用程序开发\刷题\question_images\image_mapping.json', 'r', encoding='utf-8') as f:
    img_mapping = json.load(f)

# 添加剩余3道
for qid in ['813', '996', '1077']:
    if qid not in img_mapping:
        # 找对应的裁剪文件
        for f in os.listdir(r'D:\应用程序开发\刷题\question_images'):
            if f.startswith(f'id{qid}_') and f.endswith('_crop.png'):
                img_mapping[qid] = [f]
                print(f"添加 id={qid}: {f}")
                break

print(f"总匹配题目数: {len(img_mapping)}")

# 保存映射
with open(r'D:\应用程序开发\刷题\question_images\image_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(img_mapping, f, ensure_ascii=False, indent=2)

# 更新JSON
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

updated = 0
for q in data:
    qid = str(q['id'])
    if qid in img_mapping:
        qtext = re.sub(r'【本题配图，PDF第\d+页】', '', q['question'])
        qtext = re.sub(r'【配图：[^】]+】', '', qtext)
        qtext = qtext.strip()
        img_files = img_mapping[qid]
        if len(img_files) == 1:
            img_tag = f"【配图：{img_files[0]}】"
        else:
            img_tag = f"【配图：{', '.join(img_files)}】"
        q['question'] = qtext + img_tag
        updated += 1

print(f"已更新 {updated} 道题的配图信息")

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 统计
img_keywords = ['如图', '图所示', '图中', '下图', '上图', '图示', '见图', '图为', '图是']
still_unmatched = []
for q in data:
    if any(kw in q['question'] for kw in img_keywords):
        qid = str(q['id'])
        if qid not in img_mapping:
            still_unmatched.append(q['id'])

print(f"仍未匹配配图的题目: {len(still_unmatched)}道")
if still_unmatched:
    print(f"  id: {still_unmatched}")
