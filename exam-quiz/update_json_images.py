import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

# 加载图片映射
with open(r'D:\应用程序开发\刷题\question_images\image_mapping.json', 'r', encoding='utf-8') as f:
    img_mapping = json.load(f)

# 加载JSON
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

updated = 0
for q in data:
    qid = str(q['id'])
    if qid in img_mapping:
        # 移除旧的【本题配图，PDF第XX页】标记
        qtext = re.sub(r'【本题配图，PDF第\d+页】', '', q['question']).strip()
        # 添加图片文件名标记
        img_files = img_mapping[qid]
        if len(img_files) == 1:
            img_tag = f"【配图：{img_files[0]}】"
        else:
            img_tag = f"【配图：{', '.join(img_files)}】"
        q['question'] = qtext + img_tag
        updated += 1

print(f"已更新 {updated} 道题的配图信息")
print(f"未匹配图片的需配图题目仍保留【本题配图，PDF第XX页】标记")

# 保存
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON已保存")

# 验证几道题
for q in data:
    if q['id'] in [64, 312, 322]:
        print(f"\nid={q['id']} ({q['year']}):")
        print(f"  question: {q['question'][:120]}")
