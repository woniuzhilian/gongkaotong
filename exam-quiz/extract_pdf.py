import pdfplumber
import json
import re
import os

def extract_pdf_text(pdf_path, output_txt):
    """提取PDF全部文本，带页码标记"""
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            all_text.append(f"===PAGE_{i+1}===")
            all_text.append(text)
            if (i+1) % 50 == 0:
                print(f"  已提取 {i+1}/{total} 页")
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_text))
    print(f"完成: {output_txt}")

# 提取题目PDF
print("提取题目PDF...")
extract_pdf_text(
    r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf',
    r'D:\应用程序开发\刷题\questions_raw.txt'
)

# 提取答案PDF
print("提取答案PDF...")
extract_pdf_text(
    r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_答案解析.pdf',
    r'D:\应用程序开发\刷题\answers_raw.txt'
)

print("全部提取完成")
