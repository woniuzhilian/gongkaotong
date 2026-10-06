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

# 从原始文本找每道题的页码
pages_text = re.split(r'===PAGE_(\d+)===', raw_text)
id_to_page = {}
qid_counter = 0
for i in range(1, len(pages_text), 2):
    page_num = int(pages_text[i])
    page_content = pages_text[i+1]
    page_matches = list(pattern.finditer(page_content))
    for m in page_matches:
        qid_counter += 1
        year = m.group(1).replace(' ', '')
        qnum = m.group(2)
        if year == '2016' and qnum == '66' and qid_counter > skip_pos:
            qid_counter -= 1
            continue
        id_to_page[qid_counter] = page_num

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

output_dir = r'D:\应用程序开发\刷题\question_images'
os.makedirs(output_dir, exist_ok=True)

def find_question_position(page, qnum):
    """找到题目标记在页面上的位置"""
    search_texts = [f"【{qnum}】", f"【 {qnum} 】"]
    for st in search_texts:
        rects = page.search_for(st)
        if rects:
            return rects[0]
    # 用题号数字搜索
    parts = qnum.split('-')
    if len(parts) == 2:
        rects = page.search_for(parts[1])
        if rects:
            return rects[0]
    return None

def find_options_position(page):
    """找到选项（A）（B）（C）（D）在页面上的位置"""
    for opt in ["（A）", "(A)"]:
        rects = page.search_for(opt)
        if rects:
            # 返回最靠上的选项位置
            return min(rects, key=lambda r: r.y0)
    return None

def find_next_question(page, current_y):
    """找到下一道题的位置"""
    all_marks = []
    for m in pattern.finditer(page.get_text()):
        mark_text = m.group(0).strip()
        rects = page.search_for(mark_text)
        if rects:
            all_marks.append(rects[0].y0)
    all_marks.sort()
    for y in all_marks:
        if y > current_y + 5:
            return y
    return page.rect.height

# 批量处理
success = 0
failed = []
for u in unmatched:
    qid = u['id']
    qnum = u['qnum']
    page_num = u['page']
    if not page_num:
        failed.append((qid, qnum, '无页码'))
        continue

    # 先在题干页找选项位置
    page = doc[page_num - 1]
    q_rect = find_question_position(page, qnum)
    if not q_rect:
        failed.append((qid, qnum, f'第{page_num}页未找到题目标记'))
        continue

    # 找选项位置
    opt_rect = find_options_position(page)

    # 如果当前页没有选项，检查下一页
    img_page_num = page_num
    if not opt_rect or opt_rect.y0 < q_rect.y1:
        # 选项可能在下一页
        if page_num < len(doc):
            next_page = doc[page_num]
            opt_rect = find_options_position(next_page)
            if opt_rect:
                img_page_num = page_num + 1
                page = next_page

    if not opt_rect:
        failed.append((qid, qnum, '未找到选项位置'))
        continue

    # 图形区域：从题干下方（或页面顶部）到选项上方
    if img_page_num == page_num:
        # 同页：题干下方到选项上方
        clip_top = q_rect.y1 + 2
    else:
        # 跨页：下一页顶部到选项上方
        clip_top = 10

    clip_bottom = opt_rect.y0 - 2
    if clip_bottom - clip_top < 15:
        failed.append((qid, qnum, f'裁剪区域太小({clip_bottom-clip_top:.1f})'))
        continue

    # 裁剪渲染
    clip_rect = pymupdf.Rect(0, clip_top, page.rect.width, clip_bottom)
    mat = pymupdf.Matrix(3, 3)
    pix = page.get_pixmap(matrix=mat, clip=clip_rect)

    img_filename = f"id{qid}_{qnum.replace('-', '_')}_crop.png"
    img_path = os.path.join(output_dir, img_filename)
    pix.save(img_path)
    success += 1

print(f"\n成功裁剪: {success}道")
print(f"失败: {len(failed)}道")
for qid, qnum, reason in failed[:15]:
    print(f"  id={qid}, {qnum}: {reason}")

doc.close()
