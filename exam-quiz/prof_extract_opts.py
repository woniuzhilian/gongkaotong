import sys, json, re, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_merged_full.json', 'r', encoding='utf-8') as f:
    full_data = json.load(f)

with open(r'D:\应用程序开发\刷题\prof_opt_locations.json', 'r', encoding='utf-8') as f:
    locations = json.load(f)

q_pdf = r'D:\证件相关\一级岩土工程师\真题空白卷\岩土专业基础历年真题试题册（2024版）.pdf'
doc = pymupdf.open(q_pdf)

out_dir = r'D:\应用程序开发\刷题\prof_option_images'
os.makedirs(out_dir, exist_ok=True)

# 找出选项为空的题目
empty_opt_questions = []
for q in full_data:
    empty_opts = [opt for opt in ['A', 'B', 'C', 'D'] if q[opt] == '']
    if empty_opts and q['year'] != '2024':
        empty_opt_questions.append(q)

print(f"处理{len(empty_opt_questions)}道题（2016-2023年）")

extracted = 0
for q in empty_opt_questions:
    qid = str(q['id'])
    if qid not in locations:
        continue
    
    page_idx, year, qnum = locations[qid]
    page = doc[page_idx]
    
    # 搜索当前题号
    qnum_str = str(qnum)
    # 尝试多种题号格式
    search_patterns = [
        f"{qnum_str}、",
        f"{qnum_str}.",
        f"{qnum_str}．",
    ]
    
    current_rect = None
    for pat in search_patterns:
        rects = page.search_for(pat)
        if rects:
            current_rect = rects[0]
            break
    
    if not current_rect:
        print(f"  id={qid}, {year}年第{qnum}题: 未找到题号位置")
        continue
    
    # 搜索下一题号
    next_qnum = qnum + 1
    next_rect = None
    for pat in [f"{next_qnum}、", f"{next_qnum}.", f"{next_qnum}．"]:
        rects = page.search_for(pat)
        if rects:
            next_rect = rects[0]
            break
    
    # 如果下一题不在本页，用页面底部
    if next_rect:
        clip_bottom = next_rect.y0 - 5
    else:
        clip_bottom = page.rect.height - 50  # 减去页脚
    
    # 裁剪从题号下方到下一题号上方的区域（包含题干和选项）
    clip_rect = pymupdf.Rect(
        50,  # 左边距
        current_rect.y0 - 5,
        page.rect.width - 50,  # 右边距
        clip_bottom
    )
    
    # 渲染
    mat = pymupdf.Matrix(2.5, 2.5)
    pix = page.get_pixmap(matrix=mat, clip=clip_rect)
    
    img_path = os.path.join(out_dir, f'q{qid}_{year}_{qnum}.png')
    pix.save(img_path)
    extracted += 1
    print(f"  id={qid}, {year}年第{qnum}题: 已提取 -> {os.path.basename(img_path)}")

doc.close()
print(f"\n共提取{extracted}道题的选项区域图片")
