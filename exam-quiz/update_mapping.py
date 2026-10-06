import json, sys, re, os
sys.stdout.reconfigure(encoding='utf-8')

# 加载已有映射
with open(r'D:\应用程序开发\刷题\question_images\image_mapping.json', 'r', encoding='utf-8') as f:
    img_mapping = json.load(f)

# 扫描裁剪出来的图片
output_dir = r'D:\应用程序开发\刷题\question_images'
crop_files = [f for f in os.listdir(output_dir) if f.endswith('_crop.png')]

# 从文件名提取id
added = 0
for fname in crop_files:
    m = re.match(r'id(\d+)_', fname)
    if m:
        qid = m.group(1)
        if qid not in img_mapping:
            img_mapping[qid] = [fname]
            added += 1
        else:
            # 已有图片，追加裁剪图
            if fname not in img_mapping[qid]:
                img_mapping[qid].append(fname)
                added += 1

print(f"新增图片映射: {added}个")
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
        # 移除旧的配图标记和PDF页码标记
        qtext = re.sub(r'【本题配图，PDF第\d+页】', '', q['question'])
        qtext = re.sub(r'【配图：[^】]+】', '', qtext)
        qtext = qtext.strip()
        # 添加新的配图标记
        img_files = img_mapping[qid]
        if len(img_files) == 1:
            img_tag = f"【配图：{img_files[0]}】"
        else:
            img_tag = f"【配图：{', '.join(img_files)}】"
        q['question'] = qtext + img_tag
        updated += 1

print(f"已更新 {updated} 道题的配图信息")

# 保存JSON
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 统计仍未匹配的题目
img_keywords = ['如图', '图所示', '图中', '下图', '上图', '图示', '见图', '图为', '图是']
still_unmatched = []
for q in data:
    if any(kw in q['question'] for kw in img_keywords):
        qid = str(q['id'])
        if qid not in img_mapping:
            still_unmatched.append(q['id'])

print(f"仍未匹配配图的题目: {len(still_unmatched)}道")
print(f"  id: {still_unmatched}")
