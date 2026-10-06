import sys, re, os, json
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf'
doc = pymupdf.open(pdf_path)

# 建立id到题号的映射
with open(r'D:\应用程序开发\刷题\questions_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()
pattern = re.compile(r'【\s*(\d{4}\s*补?)\s*-\s*(\d+)\s*】')
matches = list(pattern.finditer(raw_text))
dup_positions = []
for i, m in enumerate(matches):
    year = m.group(1).replace(' ', '')
    qnum = m.group(2)
    if year == '2016' and qnum == '66':
        dup_positions.append(i+1)
skip_pos = dup_positions[1] if len(dup_positions) > 1 else 819

id_to_qnum = {}
for qid in range(1, 1439):
    if qid < skip_pos:
        match_idx = qid - 1
    else:
        match_idx = qid
    m = matches[match_idx]
    year = m.group(1).replace(' ', '')
    qnum = m.group(2)
    id_to_qnum[qid] = f"{year}-{qnum}"

# 加载JSON
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 需配图的题目id集合
img_keywords = ['如图', '图所示', '图中', '下图', '上图', '图示', '见图', '图为', '图是']
need_img_ids = set()
for q in data:
    if any(kw in q['question'] for kw in img_keywords):
        need_img_ids.add(q['id'])

print(f"需配图题目: {len(need_img_ids)}道")

# 创建输出目录
output_dir = r'D:\应用程序开发\刷题\question_images'
os.makedirs(output_dir, exist_ok=True)

# 遍历每一页，提取图片并与题目对应
question_images = {}  # id -> list of image paths
unmatched_images = []
matched_count = 0

for page_num in range(len(doc)):
    page = doc[page_num]
    page_label = page_num + 1

    # 获取页面上所有图片的位置
    image_list = page.get_images(full=True)
    if not image_list:
        continue

    # 获取每张图片的位置bbox
    img_positions = []
    for img_idx, img in enumerate(image_list):
        xref = img[0]
        # 获取图片在页面上的位置
        rects = page.get_image_rects(xref)
        if rects:
            bbox = rects[0]
            img_positions.append({
                'xref': xref,
                'idx': img_idx,
                'y0': bbox.y0,
                'y1': bbox.y1,
                'x0': bbox.x0,
                'x1': bbox.x1,
                'width': img[2],
                'height': img[3]
            })

    if not img_positions:
        continue

    # 按y0排序（从上到下）
    img_positions.sort(key=lambda x: x['y0'])

    # 获取页面上所有题目标记的位置
    # 搜索【年份-题号】格式
    text_instances = []
    for qid in need_img_ids:
        qnum = id_to_qnum.get(qid, '')
        if not qnum:
            continue
        # 搜索题目标记
        search_text = f"【{qnum}】"
        rects = page.search_for(search_text)
        if not rects:
            # 尝试带空格的格式
            search_text2 = f"【 {qnum} 】"
            rects = page.search_for(search_text2)
        if rects:
            text_instances.append({
                'id': qid,
                'qnum': qnum,
                'y0': rects[0].y0,
                'y1': rects[0].y1
            })

    # 按y0排序
    text_instances.sort(key=lambda x: x['y0'])

    # 将图片分配给题目：图片在题目下方，且在下一道题上方
    for i, ti in enumerate(text_instances):
        qid = ti['id']
        # 这道题的下方范围：从题目y1到下一道题的y0（或页面底部）
        top = ti['y1']
        bottom = text_instances[i+1]['y0'] if i+1 < len(text_instances) else page.rect.height

        # 找在这个范围内的图片
        assigned = []
        for img in img_positions:
            # 图片的中心在题目范围内，或者图片大部分在范围内
            img_center_y = (img['y0'] + img['y1']) / 2
            if top - 10 <= img_center_y <= bottom + 10:
                assigned.append(img)

        if assigned:
            for img in assigned:
                # 提取图片
                base_image = doc.extract_image(img['xref'])
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                qnum = id_to_qnum.get(qid, '')
                img_filename = f"id{qid}_{qnum.replace('-', '_')}_{img['idx']+1}.{image_ext}"
                img_path = os.path.join(output_dir, img_filename)
                with open(img_path, "wb") as f:
                    f.write(image_bytes)

                if qid not in question_images:
                    question_images[qid] = []
                question_images[qid].append(img_filename)
                matched_count += 1

# 统计
print(f"\n成功匹配图片的题目: {len(question_images)}道")
print(f"提取图片总数: {matched_count}张")
print(f"未匹配到图片的需配图题目: {len(need_img_ids) - len(question_images)}道")

# 列出未匹配的题目
unmatched = need_img_ids - set(question_images.keys())
if unmatched:
    print(f"\n未匹配到图片的题目（前20个）:")
    for qid in sorted(unmatched)[:20]:
        qnum = id_to_qnum.get(qid, '?')
        q = next((x for x in data if x['id'] == qid), None)
        if q:
            qclean = re.sub(r'【本题配图，PDF第\d+页】', '', q['question']).strip()
            print(f"  id={qid}, {qnum}, {q['smallSubject']}: {qclean[:40]}")

# 保存映射关系
mapping_path = os.path.join(output_dir, 'image_mapping.json')
with open(mapping_path, 'w', encoding='utf-8') as f:
    json.dump(question_images, f, ensure_ascii=False, indent=2)
print(f"\n映射关系已保存: {mapping_path}")

doc.close()
