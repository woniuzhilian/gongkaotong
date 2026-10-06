import sys, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

q_pdf = r'D:\应用程序开发\刷题\题目和答案pdf\岩土专业基础分类真题解析（16~24）_题目.pdf'
doc = pymupdf.open(q_pdf)

out_dir = r'D:\应用程序开发\刷题\prof_option_images'
os.makedirs(out_dir, exist_ok=True)

# 2024年题目: (id, qnum, page)
questions_2024 = [
    (560, 24, 56),
    (562, 26, 60),
    (563, 27, 54),
    (575, 39, 39),
    (591, 55, 42),
]

for qid, qnum, page_num in questions_2024:
    page = doc[page_num - 1]  # 0-indexed
    
    # 搜索题号标记 【2024-XX】
    pattern = f'【2024-{qnum}】'
    rects = page.search_for(pattern)
    
    if not rects:
        # 尝试只搜索年份
        pattern = f'2024-{qnum}'
        rects = page.search_for(pattern)
    
    if not rects:
        print(f"id={qid}, 2024-{qnum}, 第{page_num}页: 未找到题号")
        # 渲染整页
        mat = pymupdf.Matrix(2.5, 2.5)
        pix = page.get_pixmap(matrix=mat)
        img_path = os.path.join(out_dir, f'q{qid}_2024_{qnum}.png')
        pix.save(img_path)
        print(f"  渲染整页 -> {os.path.basename(img_path)}")
        continue
    
    current_rect = rects[0]
    
    # 搜索下一题号
    next_qnum = qnum + 1
    next_rect = None
    for pat in [f'【2024-{next_qnum}】', f'2024-{next_qnum}']:
        r = page.search_for(pat)
        if r:
            next_rect = r[0]
            break
    
    if next_rect:
        clip_bottom = next_rect.y0 - 5
    else:
        clip_bottom = page.rect.height - 50
    
    # 裁剪题目区域
    clip_rect = pymupdf.Rect(
        30,
        current_rect.y0 - 5,
        page.rect.width - 30,
        clip_bottom
    )
    
    mat = pymupdf.Matrix(2.5, 2.5)
    pix = page.get_pixmap(matrix=mat, clip=clip_rect)
    
    img_path = os.path.join(out_dir, f'q{qid}_2024_{qnum}.png')
    pix.save(img_path)
    print(f"id={qid}, 2024-{qnum}, 第{page_num}页: 已提取 -> {os.path.basename(img_path)}")

doc.close()
print("\n2024年题目提取完成")
