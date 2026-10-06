import sys, json, re, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

q_pdf = r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf'
doc = pymupdf.open(q_pdf)

out_dir = r'D:\应用程序开发\刷题\pub_option_images'

# 手动指定搜索关键词
manual_searches = [
    (9, '2013', '均可微'),
    (250, '2016', '等于'),
    (252, '2016', '常数'),
    (569, '2018', None),  # 已知页码220
    (721, '2020', '向量'),
]

for qid, year, keyword in manual_searches:
    if qid == 569:
        # 已知页码220
        page = doc[219]  # 0-indexed
        # 搜索"图"字
        rects = page.search_for('图')
        if rects:
            current_rect = rects[0]
        else:
            current_rect = pymupdf.Rect(50, 100, 500, 200)
    else:
        # 在所有页面搜索关键词
        found = False
        for pg in range(len(doc)):
            rects = doc[pg].search_for(keyword)
            if rects:
                page = doc[pg]
                current_rect = rects[0]
                found = True
                break
        if not found:
            print(f"id={qid}: 未找到关键词'{keyword}'")
            continue
    
    clip_bottom = page.rect.height - 50
    clip_rect = pymupdf.Rect(
        30,
        current_rect.y0 - 10,
        page.rect.width - 30,
        clip_bottom
    )
    
    mat = pymupdf.Matrix(2.5, 2.5)
    pix = page.get_pixmap(matrix=mat, clip=clip_rect)
    
    img_path = os.path.join(out_dir, f'q{qid}_{year}.png')
    pix.save(img_path)
    print(f"id={qid}, {year}: 已提取 -> {os.path.basename(img_path)}")

doc.close()
print("\n完成")
