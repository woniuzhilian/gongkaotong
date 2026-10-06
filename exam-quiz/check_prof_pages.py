import sys, re, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r'D:\应用程序开发\刷题\题目和答案pdf\岩土专业基础分类真题解析（16~24）_题目.pdf'
doc = pymupdf.open(pdf_path)

# 渲染几页看看13-16题的情况
# 先看第1页（2016年开始，应该有1-12题）
out_dir = r'D:\应用程序开发\刷题\prof_check'
os.makedirs(out_dir, exist_ok=True)

# 渲染第1-4页
for pg in [0, 1, 2, 3]:
    mat = pymupdf.Matrix(2, 2)
    pix = doc[pg].get_pixmap(matrix=mat)
    pix.save(os.path.join(out_dir, f'page_{pg+1}.png'))
    print(f"已渲染第{pg+1}页")

# 检查2014年的题目在哪一页
with open(r'D:\应用程序开发\刷题\prof_questions_raw.txt', 'r', encoding='utf-8') as f:
    raw = f.read()
pages = re.split(r'===PAGE_(\d+)===', raw)
for i in range(1, len(pages), 2):
    pg = int(pages[i])
    content = pages[i+1]
    if '2014' in content:
        print(f"\n2014年题目在第{pg}页:")
        print(content[:500])

doc.close()
