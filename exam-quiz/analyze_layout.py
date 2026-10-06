import sys, re, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf'
doc = pymupdf.open(pdf_path)

# 分析id=555 (2013-49, PDF84页) 的页面布局
page = doc[83]  # 0-based
print(f"页面尺寸: {page.rect.width} x {page.rect.height}")

# 获取所有文本块
blocks = page.get_text("blocks")
print(f"\n页面文本块数: {len(blocks)}")
print("\n所有文本块（按y排序）:")
sorted_blocks = sorted(blocks, key=lambda b: b[1])
for i, block in enumerate(sorted_blocks):
    x0, y0, x1, y1, text, block_no, block_type = block
    text_clean = text.strip().replace('\n', ' ')[:60]
    if text_clean:
        print(f"  块{i}: x={x0:.0f}-{x1:.0f}, y={y0:.0f}-{y1:.0f}: {text_clean}")

# 找2013-49的位置
print("\n=== 搜索2013-49 ===")
rects = page.search_for("【2013-49】")
for r in rects:
    print(f"  题号位置: x={r.x0:.0f}-{r.x1:.0f}, y={r.y0:.0f}-{r.y1:.0f}")

# 找选项位置
print("\n=== 搜索选项 ===")
for opt in ["（A）", "（B）", "（C）", "（D）"]:
    rects = page.search_for(opt)
    for r in rects:
        if r.y0 > 600:  # 在题目附近
            print(f"  {opt}: x={r.x0:.0f}-{r.x1:.0f}, y={r.y0:.0f}-{r.y1:.0f}")

# 渲染整页看看
mat = pymupdf.Matrix(2, 2)
pix = page.get_pixmap(matrix=mat)
pix.save(r'D:\应用程序开发\刷题\page84_full.png')
print(f"\n整页已保存: page84_full.png")

doc.close()
