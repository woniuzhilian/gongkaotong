import sys, json, re, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    pub = json.load(f)

q_pdf = r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf'
doc = pymupdf.open(q_pdf)

out_dir = r'D:\应用程序开发\刷题\pub_option_images'
os.makedirs(out_dir, exist_ok=True)

# 找出空选项的题目
empty_opt_questions = []
for q in pub:
    empty_opts = [opt for opt in ['A', 'B', 'C', 'D'] if q[opt] == '']
    if empty_opts:
        empty_opt_questions.append(q)

print(f"处理{len(empty_opt_questions)}道题")

# 建立年份到起始页的映射
year_pages = {}
current_year = None
for i in range(len(doc)):
    text = doc[i].get_text()
    # 匹配年份标题
    for year in ['2013', '2014', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']:
        if f'{year}年' in text and '注册' in text:
            if year not in year_pages:
                year_pages[year] = i
                break
    # 2022补考
    if '2022年（补考）' in text or '2022年(补考)' in text:
        if '2022补' not in year_pages:
            year_pages['2022补'] = i

print(f"年份起始页: {year_pages}")

extracted = 0
failed = []

for q in empty_opt_questions:
    qid = q['id']
    year = q['year']
    
    # 从题干中提取题号
    qnum_match = re.search(r'【(\d{4})-(\d+)】', q['question'])
    if qnum_match:
        qnum = int(qnum_match.group(2))
    else:
        # 尝试从题干开头提取
        qnum_match = re.match(r'^(\d{1,3})[、.．]', q['question'])
        if qnum_match:
            qnum = int(qnum_match.group(1))
        else:
            failed.append((qid, '无法提取题号'))
            continue
    
    # 确定年份范围
    if year not in year_pages:
        failed.append((qid, f'年份{year}未找到起始页'))
        continue
    
    start_page = year_pages[year]
    # 找下一个年份
    next_years = [p for y, p in year_pages.items() if p > start_page]
    end_page = min(next_years) if next_years else len(doc)
    
    # 在页面范围内查找题号
    found = False
    for pg in range(start_page, end_page):
        page = doc[pg]
        text = page.get_text()
        
        # 搜索题号标记
        patterns = [
            f'【{year}-{qnum}】',
            f'{year}-{qnum}',
            f'{qnum}、',
        ]
        
        current_rect = None
        for pat in patterns:
            rects = page.search_for(pat)
            if rects:
                current_rect = rects[0]
                break
        
        if current_rect:
            # 找下一题号
            next_qnum = qnum + 1
            next_rect = None
            for pat in [f'【{year}-{next_qnum}】', f'{year}-{next_qnum}', f'{next_qnum}、']:
                rects = page.search_for(pat)
                if rects:
                    next_rect = rects[0]
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
            
            img_path = os.path.join(out_dir, f'q{qid}_{year}_{qnum}.png')
            pix.save(img_path)
            extracted += 1
            found = True
            break
    
    if not found:
        failed.append((qid, f'{year}年第{qnum}题未找到'))

doc.close()
print(f"\n成功提取{extracted}道题")
if failed:
    print(f"失败{len(failed)}道:")
    for qid, reason in failed:
        print(f"  id={qid}: {reason}")

# 保存失败列表
with open(r'D:\应用程序开发\刷题\pub_opt_extract_failed.json', 'w', encoding='utf-8') as f:
    json.dump(failed, f, ensure_ascii=False, indent=2)
