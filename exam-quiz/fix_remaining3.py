import sys, re, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf'
doc = pymupdf.open(pdf_path)

# 建立id到题号和页码的映射
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

output_dir = r'D:\应用程序开发\刷题\question_images'

# 处理3道未匹配的题目
for qid in [813, 996, 1077]:
    qnum = id_to_qnum.get(qid, '')
    page_num = id_to_page.get(qid, None)
    print(f"\n=== id={qid}, {qnum}, PDF第{page_num}页 ===")

    if not page_num:
        print("  无页码")
        continue

    # 渲染整页的上半部分和下半部分看看
    page = doc[page_num - 1]
    mat = pymupdf.Matrix(2, 2)

    # 先保存整页看看
    pix = page.get_pixmap(matrix=mat)
    full_path = os.path.join(output_dir, f"id{qid}_full_page.png")
    pix.save(full_path)
    print(f"  整页已保存: {full_path}")

    # 打印页面文本
    text = page.get_text()
    print(f"  页面文本前300字: {text[:300]}")

doc.close()
