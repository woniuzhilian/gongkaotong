import sys, fitz  # PyMuPDF
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf'
doc = fitz.open(pdf_path)

print(f"PDF总页数: {len(doc)}")

# 统计每页的图片数量
total_images = 0
pages_with_images = []
for page_num in range(len(doc)):
    page = doc[page_num]
    images = page.get_images(full=True)
    if images:
        total_images += len(images)
        pages_with_images.append((page_num + 1, len(images)))

print(f"总图片数: {total_images}")
print(f"含图片的页数: {len(pages_with_images)}")
print(f"\n前20页含图片的页面:")
for page, count in pages_with_images[:20]:
    print(f"  第{page}页: {count}张图")

# 看看第45页（用户提到的2019-28所在页）的图片情况
print(f"\n=== 第45页详情 ===")
page = doc[44]  # 0-based
images = page.get_images(full=True)
print(f"图片数: {len(images)}")
for i, img in enumerate(images):
    xref = img[0]
    print(f"  图片{i+1}: xref={xref}, width={img[2]}, height={img[3]}")

# 提取第45页的图片保存看看
import os
output_dir = r'D:\应用程序开发\刷题\extracted_images'
os.makedirs(output_dir, exist_ok=True)

for i, img in enumerate(images):
    xref = img[0]
    base_image = doc.extract_image(xref)
    image_bytes = base_image["image"]
    image_ext = base_image["ext"]
    img_path = os.path.join(output_dir, f"page45_img{i+1}.{image_ext}")
    with open(img_path, "wb") as f:
        f.write(image_bytes)
    print(f"  已保存: {img_path} ({len(image_bytes)} bytes)")

doc.close()
