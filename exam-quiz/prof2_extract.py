import sys, re, os
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

def extract_pdf_text(pdf_path, output_txt):
    doc = pymupdf.open(pdf_path)
    all_text = []
    for i in range(len(doc)):
        text = doc[i].get_text()
        all_text.append(f"===PAGE_{i+1}===\n{text}")
    total = len(doc)
    doc.close()
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_text))
    print(f"已提取: {output_txt} ({total}页)")

# 提取试题册
q_pdf = r'D:\证件相关\一级岩土工程师\真题空白卷\岩土专业基础历年真题试题册（2024版）.pdf'
extract_pdf_text(q_pdf, r'D:\应用程序开发\刷题\prof2_questions_raw.txt')

# 提取解析册
a_pdf = r'D:\证件相关\一级岩土工程师\真题空白卷\岩土专业基础历年真题解析册（2024版）.pdf'
extract_pdf_text(a_pdf, r'D:\应用程序开发\刷题\prof2_answers_raw.txt')
