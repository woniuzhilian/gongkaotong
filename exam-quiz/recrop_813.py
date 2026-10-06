import sys, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf'
doc = pymupdf.open(pdf_path)
output_dir = r'D:\应用程序开发\刷题\question_images'
mat = pymupdf.Matrix(3, 3)

# id=813 (2022补-68), PDF159页
page = doc[158]
# 先打印页面上所有文本块的位置，找到图形区域
blocks = page.get_text("blocks")
print("页面文本块（y>450）:")
for b in sorted(blocks, key=lambda x: x[1]):
    if b[1] > 450:
        x0, y0, x1, y1, text = b[:5]
        print(f"  y={y0:.0f}-{y1:.0f}: {text.strip()[:50]}")

# 图形应该在"【2022 补-68】"和选项之间
# 从文本块看，找题目和选项的位置
q_rect = page.search_for("【2022 补-68】")
if q_rect:
    print(f"\n题目位置: y={q_rect[0].y0:.0f}-{q_rect[0].y1:.0f}")

opt_rect = page.search_for("（A）")
for r in opt_rect:
    if r.y0 > 500:
        print(f"选项位置: y={r.y0:.0f}-{r.y1:.0f}")
        # 裁剪题目下方到选项上方
        clip_top = q_rect[0].y1 + 5
        clip_bottom = r.y0 - 5
        print(f"裁剪区域: y={clip_top:.0f}-{clip_bottom:.0f}")
        clip_rect = pymupdf.Rect(80, clip_top, 520, clip_bottom)
        pix = page.get_pixmap(matrix=mat, clip=clip_rect)
        pix.save(os.path.join(output_dir, 'id813_2022补_68_crop.png'))
        print(f"已重新裁剪: {pix.width}x{pix.height}")
        break

doc.close()
