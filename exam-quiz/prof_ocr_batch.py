import sys, os, re, json
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

# 使用Python3.12的rapidocr
sys.path.insert(0, r'C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages')
from rapidocr_onnxruntime import RapidOCR

ocr = RapidOCR()

def ocr_pdf(pdf_path, output_txt, batch_size=10):
    """批量OCR识别PDF，保存为带页码标记的文本"""
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    print(f"开始OCR: {pdf_path} ({total_pages}页)")

    all_text = []
    for i in range(total_pages):
        page = doc[i]
        # 渲染为高清图片
        mat = pymupdf.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        img_path = os.path.join(os.environ.get('TEMP', '.'), f'_ocr_page_{i}.png')
        pix.save(img_path)

        # OCR识别
        result, elapse = ocr(img_path)

        page_text = []
        if result:
            # 按y坐标排序，保持阅读顺序
            result_sorted = sorted(result, key=lambda x: (x[0][0][1], x[0][0][0]))
            for line in result_sorted:
                page_text.append(line[1])

        # 清理临时文件
        os.remove(img_path)

        page_content = '\n'.join(page_text)
        all_text.append(f"===PAGE_{i+1}===\n{page_content}")

        if (i+1) % 10 == 0:
            print(f"  已完成 {i+1}/{total_pages} 页")

    doc.close()

    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_text))

    print(f"完成: {output_txt}")
    return total_pages

# OCR题目PDF
q_pdf = r'D:\应用程序开发\刷题\题目和答案pdf\岩土专业基础分类真题解析（16~24）_题目.pdf'
q_txt = r'D:\应用程序开发\刷题\prof_questions_raw.txt'
ocr_pdf(q_pdf, q_txt)

# OCR答案PDF
a_pdf = r'D:\应用程序开发\刷题\题目和答案pdf\岩土专业基础分类真题解析（16~24）_答案解析.pdf'
a_txt = r'D:\应用程序开发\刷题\prof_answers_raw.txt'
ocr_pdf(a_pdf, a_txt)

print("全部OCR完成!")
