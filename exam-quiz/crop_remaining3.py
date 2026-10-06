import sys, re, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf'
doc = pymupdf.open(pdf_path)
output_dir = r'D:\应用程序开发\刷题\question_images'
mat = pymupdf.Matrix(3, 3)

# id=813 (2022补-68), PDF159页，图形在4个单元体应力状态图
page = doc[158]  # 0-based
# 图形区域：y约480-590
clip_rect = pymupdf.Rect(80, 475, 520, 590)
pix = page.get_pixmap(matrix=mat, clip=clip_rect)
pix.save(os.path.join(output_dir, 'id813_2022补_68_crop.png'))
print(f"id=813: 已裁剪 ({pix.width}x{pix.height})")

# id=996 (2022补-84), 先看204页
page204 = doc[203]
text204 = page204.get_text()
print(f"\n第204页文本前500字:\n{text204[:500]}")

# 找2022补-84的位置
rects = page204.search_for("2022 补-84")
if rects:
    print(f"2022补-84在第204页, y={rects[0].y0:.1f}")
    # 找选项位置
    opt_rects = page204.search_for("（A）")
    if opt_rects:
        # 找在题目下方的选项
        for opt in opt_rects:
            if opt.y0 > rects[0].y1:
                print(f"选项位置: y={opt.y0:.1f}")
                # 裁剪题目下方到选项上方
                clip_rect = pymupdf.Rect(80, rects[0].y1 + 2, 520, opt.y0 - 2)
                pix = page204.get_pixmap(matrix=mat, clip=clip_rect)
                pix.save(os.path.join(output_dir, 'id996_2022补_84_crop.png'))
                print(f"id=996: 已裁剪 ({pix.width}x{pix.height})")
                break

# id=1077 (2022补-88), PDF226页，图形在页面顶部（4个波形图）
# 但题干可能在上一页底部，图形是选项波形图
page226 = doc[225]
# 图形区域：页面顶部y约70-270
clip_rect = pymupdf.Rect(80, 70, 520, 270)
pix = page226.get_pixmap(matrix=mat, clip=clip_rect)
pix.save(os.path.join(output_dir, 'id1077_2022补_88_crop.png'))
print(f"\nid=1077: 已裁剪 ({pix.width}x{pix.height})")

doc.close()
print("\n完成")
