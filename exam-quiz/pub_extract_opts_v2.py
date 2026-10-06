import sys, json, re, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    pub = json.load(f)

with open(r'D:\应用程序开发\刷题\questions_raw.txt', 'r', encoding='utf-8') as f:
    raw_lines = f.readlines()

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

# 建立题干到页码的映射
# 在raw_lines中搜索题干关键词
def find_page_in_raw(question, qid):
    # 提取题干中的关键词（去掉公式和标点）
    clean_q = re.sub(r'\$[^$]*\$', '', question)
    clean_q = re.sub(r'[（）()。，、：；\s]', '', clean_q)
    keywords = clean_q[:15]
    
    if not keywords:
        return None
    
    # 在raw_lines中搜索
    current_page = None
    for i, line in enumerate(raw_lines):
        page_match = re.match(r'===PAGE_(\d+)===', line.strip())
        if page_match:
            current_page = int(page_match.group(1))
        elif keywords in line.replace(' ', ''):
            return current_page
    
    return None

extracted = 0
failed = []

for q in empty_opt_questions:
    qid = q['id']
    year = q['year']
    
    # 在原始文本中查找页码
    page_num = find_page_in_raw(q['question'], qid)
    
    if not page_num:
        failed.append((qid, '无法在原始文本中定位'))
        continue
    
    # 在PDF页面中搜索题干
    page = doc[page_num - 1]  # 0-indexed
    
    # 提取题干关键词用于搜索
    clean_q = re.sub(r'\$[^$]*\$', '', q['question'])
    clean_q = re.sub(r'[（）()。，、：；\s]', '', clean_q)
    search_text = clean_q[:10]
    
    rects = page.search_for(search_text)
    if not rects:
        # 尝试更短的关键词
        search_text = clean_q[:6]
        rects = page.search_for(search_text)
    
    if not rects:
        failed.append((qid, f'PDF第{page_num}页未找到题干'))
        continue
    
    current_rect = rects[0]
    
    # 找下一题（搜索下一个题号或下一个题干）
    # 简单方法：裁剪到页面底部
    clip_bottom = page.rect.height - 50
    
    # 裁剪题目区域
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
    extracted += 1
    
    if extracted % 10 == 0:
        print(f"  已提取{extracted}道...")

doc.close()
print(f"\n成功提取{extracted}道题")
if failed:
    print(f"失败{len(failed)}道:")
    for qid, reason in failed[:10]:
        print(f"  id={qid}: {reason}")
