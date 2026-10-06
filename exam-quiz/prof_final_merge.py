import sys, re, json, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

# 加载合并后的题目
with open(r'D:\应用程序开发\刷题\prof_all_questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

with open(r'D:\应用程序开发\刷题\prof_answers_parsed.json', 'r', encoding='utf-8') as f:
    answers = json.load(f)

# 修复2022补-41匹配
for q in questions:
    key = f"{q['year']}-{q['_qnum']}"
    if key == '2022补-41':
        if '2022-41' in answers:
            q['answer'] = answers['2022-41']['answer']
            q['analysis'] = answers['2022-41']['analysis']
            print(f"修复2022补-41: 答案={q['answer']}")

# 统计
matched = sum(1 for q in questions if q['answer'])
print(f"有答案的题目: {matched}/{len(questions)}")

# 提取题目配图
pdf_path = r'D:\应用程序开发\刷题\题目和答案pdf\岩土专业基础分类真题解析（16~24）_题目.pdf'
doc = pymupdf.open(pdf_path)
output_dir = r'D:\应用程序开发\刷题\prof_images'
os.makedirs(output_dir, exist_ok=True)

img_mapping = {}
img_keywords = ['如图', '图所示', '图中', '下图', '上图', '图示', '见图', '图为', '图是', '示意图']

# 先找所有需要配图的题目
need_img = []
for q in questions:
    if any(kw in q['question'] for kw in img_keywords):
        need_img.append(q)

print(f"需要配图的题目: {len(need_img)}道")

# 提取嵌入图片
total_extracted = 0
for page_num in range(len(doc)):
    page = doc[page_num]
    images = page.get_images(full=True)
    if not images:
        continue

    # 获取这一页的题目
    page_questions = [q for q in need_img if q['_page'] == page_num + 1]
    if not page_questions:
        continue

    for img_idx, img in enumerate(images):
        xref = img[0]
        try:
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # 获取图片在页面上的位置
            img_rects = page.get_image_rects(xref)
            if not img_rects:
                continue

            img_rect = img_rects[0]
            img_y = img_rect.y0

            # 找到这张图片属于哪道题
            # 找图片上方最近的题目标记
            best_q = None
            for q in page_questions:
                qid = q['id']
                # 找题目标记在页面上的位置
                qnum = q['_qnum']
                year = q['year'].replace('补', '')
                search_texts = [f"【{year}-{qnum}】", f"【{q['year']}-{qnum}】"]
                q_rect = None
                for st in search_texts:
                    rects = page.search_for(st)
                    if rects:
                        q_rect = rects[0]
                        break
                if q_rect and q_rect.y0 < img_y:
                    if best_q is None or q_rect.y0 > best_q[1]:
                        best_q = (q, q_rect.y0)

            if best_q:
                q = best_q[0]
                qid = q['id']
                key = str(qid)
                img_filename = f"id{qid}_{q['year']}_{q['_qnum']}_{img_idx}.{image_ext}"
                img_path = os.path.join(output_dir, img_filename)
                with open(img_path, 'wb') as f:
                    f.write(image_bytes)

                if key not in img_mapping:
                    img_mapping[key] = []
                img_mapping[key].append(img_filename)
                total_extracted += 1
        except Exception as e:
            pass

doc.close()
print(f"提取嵌入图片: {total_extracted}张，匹配{len(img_mapping)}道题")

# 保存图片映射
with open(os.path.join(output_dir, 'image_mapping.json'), 'w', encoding='utf-8') as f:
    json.dump(img_mapping, f, ensure_ascii=False, indent=2)

# 更新JSON中的配图标记
for q in questions:
    qid = str(q['id'])
    if qid in img_mapping:
        qtext = re.sub(r'【本题配图，PDF第\d+页】', '', q['question'])
        img_files = img_mapping[qid]
        img_tag = f"【配图：{', '.join(img_files)}】"
        q['question'] = qtext.strip() + img_tag
    elif any(kw in q['question'] for kw in img_keywords):
        # 未匹配的，添加页码标记
        if '【本题配图' not in q['question']:
            q['question'] += f"【本题配图，PDF第{q['_page']}页】"

# 移除内部字段
for q in questions:
    if '_qnum' in q:
        del q['_qnum']
    if '_page' in q:
        del q['_page']

# 保存最终JSON
with open(r'D:\应用程序开发\刷题\prof_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"最终题目数: {len(questions)}")
print(f"已保存 prof_questions_final.json")
