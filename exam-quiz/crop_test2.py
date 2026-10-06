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

# 从原始文本中找每道题的页码
# 按===PAGE_N===分割
pages_text = re.split(r'===PAGE_(\d+)===', raw_text)
id_to_page = {}
current_page = 0
qid_counter = 0
for i in range(1, len(pages_text), 2):
    page_num = int(pages_text[i])
    page_content = pages_text[i+1]
    # 找这一页的题目标记
    page_matches = list(pattern.finditer(page_content))
    for m in page_matches:
        qid_counter += 1
        # 跳过重复的2016-66（第二个）
        year = m.group(1).replace(' ', '')
        qnum = m.group(2)
        if year == '2016' and qnum == '66' and qid_counter > skip_pos:
            qid_counter -= 1
            continue
        id_to_page[qid_counter] = page_num

print(f"建立了 {len(id_to_page)} 道题的页码映射")

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
            page = id_to_page.get(q['id'], None)
            unmatched.append({
                'id': q['id'],
                'qnum': id_to_qnum.get(q['id'], ''),
                'page': page
            })

print(f"未匹配题目: {len(unmatched)}道")
print(f"有页码的: {sum(1 for u in unmatched if u['page'])}道")

output_dir = r'D:\应用程序开发\刷题\question_images'
os.makedirs(output_dir, exist_ok=True)

# 测试前5道
success = 0
for u in unmatched[:8]:
    qid = u['id']
    qnum = u['qnum']
    page_num = u['page']
    if not page_num:
        print(f"id={qid} 无页码，跳过")
        continue

    page = doc[page_num - 1]
    print(f"\n=== id={qid}, {qnum}, PDF第{page_num}页 ===")

    # 找题目标记位置
    search_texts = [f"【{qnum}】", f"【 {qnum} 】"]
    q_rect = None
    for st in search_texts:
        rects = page.search_for(st)
        if rects:
            q_rect = rects[0]
            break
    if not q_rect:
        print(f"  未找到题目标记位置，尝试用题号数字搜索")
        # 用题号数字搜索
        rects = page.search_for(qnum.split('-')[1])
        if rects:
            q_rect = rects[0]
        else:
            print(f"  仍未找到，跳过")
            continue

    print(f"  题目位置: y={q_rect.y0:.1f} - {q_rect.y1:.1f}")

    # 找下一道题的位置
    all_q_marks = []
    for m in pattern.finditer(page.get_text()):
        mark_text = m.group(0).strip()
        mark_rects = page.search_for(mark_text)
        if mark_rects:
            all_q_marks.append({'y0': mark_rects[0].y0, 'text': mark_text})
    all_q_marks.sort(key=lambda x: x['y0'])

    next_y = page.rect.height
    for mark in all_q_marks:
        if mark['y0'] > q_rect.y1 + 5:
            next_y = mark['y0']
            print(f"  下一题: y={mark['y0']:.1f} ({mark['text']})")
            break

    # 裁剪区域：题目下方到下一题上方
    clip_top = q_rect.y1 + 2
    clip_bottom = next_y - 2
    if clip_bottom - clip_top < 15:
        print(f"  裁剪区域太小({clip_bottom-clip_top:.1f})，跳过")
        continue

    # 直接裁剪渲染
    clip_rect = pymupdf.Rect(0, clip_top, page.rect.width, clip_bottom)
    mat = pymupdf.Matrix(3, 3)
    pix = page.get_pixmap(matrix=mat, clip=clip_rect)

    img_filename = f"id{qid}_{qnum.replace('-', '_')}_crop.png"
    img_path = os.path.join(output_dir, img_filename)
    pix.save(img_path)
    print(f"  已保存: {img_filename} ({pix.width}x{pix.height})")
    success += 1

doc.close()
print(f"\n测试完成，成功{success}道")
