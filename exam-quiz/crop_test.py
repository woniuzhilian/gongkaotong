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

# 加载已匹配的图片映射
with open(r'D:\应用程序开发\刷题\question_images\image_mapping.json', 'r', encoding='utf-8') as f:
    img_mapping = json.load(f)

# 加载JSON，找未匹配的需配图题目
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

img_keywords = ['如图', '图所示', '图中', '下图', '上图', '图示', '见图', '图为', '图是']
unmatched = []
for q in data:
    if any(kw in q['question'] for kw in img_keywords):
        qid = str(q['id'])
        if qid not in img_mapping:
            m = re.search(r'PDF第(\d+)页', q['question'])
            page = int(m.group(1)) if m else None
            unmatched.append({
                'id': q['id'],
                'qnum': id_to_qnum.get(q['id'], ''),
                'page': page
            })

print(f"未匹配题目: {len(unmatched)}道")

# 输出目录
output_dir = r'D:\应用程序开发\刷题\question_images'
os.makedirs(output_dir, exist_ok=True)

# 测试：先处理前5道，看看效果
test_count = 0
for u in unmatched[:5]:
    qid = u['id']
    qnum = u['qnum']
    page_num = u['page']
    if not page_num:
        print(f"id={qid} 无页码，跳过")
        continue

    page = doc[page_num - 1]  # 0-based
    print(f"\n=== id={qid}, {qnum}, PDF第{page_num}页 ===")

    # 找题目标记在页面上的位置
    search_text = f"【{qnum}】"
    rects = page.search_for(search_text)
    if not rects:
        search_text2 = f"【 {qnum} 】"
        rects = page.search_for(search_text2)
    if not rects:
        print(f"  未找到题目标记位置")
        continue

    q_rect = rects[0]
    print(f"  题目位置: y={q_rect.y0:.1f} - {q_rect.y1:.1f}")

    # 找下一道题的位置（在同一页或下一页）
    # 先在当前页找下一个题目标记
    all_q_marks = []
    for m in pattern.finditer(page.get_text()):
        mark_text = m.group(0)
        mark_rects = page.search_for(mark_text.strip())
        if mark_rects:
            all_q_marks.append({
                'text': mark_text,
                'y0': mark_rects[0].y0,
                'y1': mark_rects[0].y1
            })
    all_q_marks.sort(key=lambda x: x['y0'])

    # 找到当前题目的下一个题目
    next_y = page.rect.height
    for mark in all_q_marks:
        if mark['y0'] > q_rect.y1 + 5:
            next_y = mark['y0']
            print(f"  下一题位置: y={mark['y0']:.1f} ({mark['text']})")
            break

    # 裁剪区域：从题目下方到下一题上方
    # 但需要排除选项文字区域，找到真正的图形区域
    # 先获取页面上所有文本块的位置
    text_blocks = page.get_text("blocks")
    # 找到在题目和下一题之间的文本块
    blocks_in_range = []
    for block in text_blocks:
        bbox = block[:4]
        text = block[4]
        if bbox[1] > q_rect.y1 and bbox[3] < next_y:
            if text.strip():
                blocks_in_range.append({'bbox': bbox, 'text': text.strip()[:50]})

    print(f"  题目与下一题之间的文本块数: {len(blocks_in_range)}")
    for b in blocks_in_range:
        print(f"    y={b['bbox'][1]:.1f}-{b['bbox'][3]:.1f}: {b['text']}")

    # 渲染页面为高清图
    mat = pymupdf.Matrix(3, 3)  # 3倍缩放
    pix = page.get_pixmap(matrix=mat)

    # 裁剪区域：题目下方到下一题上方
    # 先试试整个区域
    clip_top = q_rect.y1 + 2
    clip_bottom = next_y - 2
    if clip_bottom - clip_top < 20:
        print(f"  裁剪区域太小，跳过")
        continue

    # 转换为像素坐标
    x0 = 0
    y0 = int(clip_top * 3)
    x1 = int(page.rect.width * 3)
    y1 = int(clip_bottom * 3)

    # 裁剪
    clip_pix = pymupdf.Pixmap(pix, pymupdf.IRect(x0, y0, x1, y1))
    img_filename = f"id{qid}_{qnum.replace('-', '_')}_crop.png"
    img_path = os.path.join(output_dir, img_filename)
    clip_pix.save(img_path)
    print(f"  已保存: {img_filename} ({clip_pix.width}x{clip_pix.height})")

    test_count += 1

doc.close()
print(f"\n测试完成，处理了{test_count}道题")
