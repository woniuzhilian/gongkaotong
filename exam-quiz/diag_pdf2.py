# -*- coding: utf-8 -*-
import sys, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
p = r"E:\应用程序开发\刷题\题目和答案pdf\岩土专业基础分类真题解析（16~24）_题目.pdf"
d = pymupdf.open(p)
print("pages", len(d))
for pg in [3,5,8,20]:
    page = d[pg]
    imgs = page.get_images(full=True)
    drawings = page.get_drawings()
    txt = page.get_text().strip()
    print(f"-- page {pg+1}: text_len={len(txt)} images={len(imgs)} drawings={len(drawings)}")
    if imgs:
        print("    img sizes:", [(i[2],i[3]) for i in imgs][:5])
