import sys, re, json, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r'D:\应用程序开发\刷题\题目和答案pdf\岩土专业基础分类真题解析（16~24）_题目.pdf'
doc = pymupdf.open(pdf_path)
output_dir = r'D:\应用程序开发\刷题\prof_images'
os.makedirs(output_dir, exist_ok=True)

with open(r'D:\应用程序开发\刷题\prof_questions_final.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

img_keywords = ['如图', '图所示', '图中', '下图', '上图', '图示', '见图', '图为', '图是', '示意图']
q_pattern = re.compile(r'【\s*(\d{4})\s*(补)?\s*-\s*(\d+)\s*】')

# 找需要配图的题目
need_img = []
for q in questions:
    if any(kw in q['question'] for kw in img_keywords) and '【配图：' not in q['question']:
        need_img.append(q)

print(f"需要裁剪配图: {len(need_img)}道")

def find_q_position(page, year, qnum):
    search_texts = [f"【{year}-{qnum}】", f"【{year.replace('补', '')}-{qnum}】", f"【{year} 补-{qnum}】"]
    for st in search_texts:
        rects = page.search_for(st)
        if rects:
            return rects[0]
    # 用题号数字搜索
    rects = page.search_for(qnum)
    if rects:
        return rects[0]
    return None

def find_options_position(page, after_y):
    for opt in ["（A）", "(A)", "（A"]:
        rects = page.search_for(opt)
        for r in rects:
            if r.y0 > after_y:
                return r
    return None

success = 0
failed = []
for q in need_img:
    qid = q['id']
    year = q['year']
    qnum = q['A']  # 不对，qnum不在字段里了
    # 从question中提取题号？不行，已经删除了_qnum
    # 我们需要重新加载带_qnum的版本
    pass

# 重新加载带内部字段的版本
with open(r'D:\应用程序开发\刷题\prof_all_questions.json', 'r', encoding='utf-8') as f:
    questions_full = json.load(f)

need_img_full = []
for q in questions_full:
    if any(kw in q['question'] for kw in img_keywords):
        need_img_full.append(q)

print(f"需要裁剪配图(完整): {len(need_img_full)}道")

for q in need_img_full:
    qid = q['id']
    year = q['year']
    qnum = q['_qnum']
    page_num = q['_page']

    page = doc[page_num - 1]
    q_rect = find_q_position(page, year, qnum)
    if not q_rect:
        failed.append((qid, f"{year}-{qnum}", '未找到题目标记'))
        continue

    # 找选项位置
    opt_rect = find_options_position(page, q_rect.y1)

    # 如果当前页没有选项，检查下一页
    img_page = page
    if not opt_rect or opt_rect.y0 < q_rect.y1:
        if page_num < len(doc):
            next_page = doc[page_num]
            opt_rect = find_options_position(next_page, 0)
            if opt_rect:
                img_page = next_page

    if not opt_rect:
        failed.append((qid, f"{year}-{qnum}", '未找到选项'))
        continue

    # 裁剪区域
    if img_page == page:
        clip_top = q_rect.y1 + 2
    else:
        clip_top = 10
    clip_bottom = opt_rect.y0 - 2

    if clip_bottom - clip_top < 15:
        failed.append((qid, f"{year}-{qnum}", f'区域太小({clip_bottom-clip_top:.1f})'))
        continue

    clip_rect = pymupdf.Rect(0, clip_top, img_page.rect.width, clip_bottom)
    mat = pymupdf.Matrix(3, 3)
    pix = img_page.get_pixmap(matrix=mat, clip=clip_rect)

    img_filename = f"id{qid}_{year}_{qnum}_crop.png"
    pix.save(os.path.join(output_dir, img_filename))
    success += 1

doc.close()
print(f"成功裁剪: {success}道")
print(f"失败: {len(failed)}道")
for qid, qnum, reason in failed:
    print(f"  id={qid}, {qnum}: {reason}")
