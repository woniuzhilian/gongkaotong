import sys, json, re, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    pub = json.load(f)

q_pdf = r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf'
doc = pymupdf.open(q_pdf)

out_dir = r'D:\应用程序开发\刷题\pub_option_images'
os.makedirs(out_dir, exist_ok=True)

# 找出空选项且尚未提取的题目
empty_opt_questions = []
for q in pub:
    empty_opts = [opt for opt in ['A', 'B', 'C', 'D'] if q[opt] == '']
    if empty_opts:
        qid = q['id']
        # 检查是否已提取
        if not os.path.exists(os.path.join(out_dir, f'q{qid}_*.png')):
            import glob
            if not glob.glob(os.path.join(out_dir, f'q{qid}_*.png')):
                empty_opt_questions.append(q)

print(f"待处理{len(empty_opt_questions)}道题")

def extract_text_keywords(question):
    """从题干中提取纯文本关键词"""
    # 去掉LaTeX公式
    text = re.sub(r'\$[^$]*\$', ' ', question)
    # 去掉配图标记
    text = re.sub(r'【[^】]*】', ' ', text)
    # 去掉标点和数字
    text = re.sub(r'[（）()。，、：；\d\s]', ' ', text)
    # 提取连续的中文字符片段
    segments = re.findall(r'[\u4e00-\u9fff]{4,}', text)
    return segments

extracted = 0
failed = []

# 预加载所有页面文本
page_texts = []
for i in range(len(doc)):
    page_texts.append(doc[i].get_text())

for q in empty_opt_questions:
    qid = q['id']
    year = q['year']
    
    keywords = extract_text_keywords(q['question'])
    if not keywords:
        failed.append((qid, '无有效关键词'))
        continue
    
    # 在所有页面中搜索
    found_page = None
    found_rect = None
    
    for pg in range(len(doc)):
        page_text = page_texts[pg]
        # 尝试每个关键词
        for kw in keywords:
            if kw in page_text:
                # 在该页搜索
                rects = doc[pg].search_for(kw)
                if rects:
                    found_page = pg
                    found_rect = rects[0]
                    break
        if found_page is not None:
            break
    
    if found_page is None:
        failed.append((qid, f'所有页面未找到，关键词={keywords[:2]}'))
        continue
    
    page = doc[found_page]
    
    # 裁剪到页面底部（包含选项）
    clip_bottom = page.rect.height - 50
    
    clip_rect = pymupdf.Rect(
        30,
        found_rect.y0 - 10,
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
print(f"\n本次提取{extracted}道题")
if failed:
    print(f"失败{len(failed)}道:")
    for qid, reason in failed[:15]:
        print(f"  id={qid}: {reason}")
