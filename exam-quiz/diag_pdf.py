# -*- coding: utf-8 -*-
import sys, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
pdfs = {
 "公共基础_题目": r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf",
 "公共基础_答案": r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_答案解析.pdf",
 "专业基础_题目": r"E:\应用程序开发\刷题\题目和答案pdf\岩土专业基础分类真题解析（16~24）_题目.pdf",
 "专业基础_答案": r"E:\应用程序开发\刷题\题目和答案pdf\岩土专业基础分类真题解析（16~24）_答案解析.pdf",
}
for name, p in pdfs.items():
    try:
        d = pymupdf.open(p)
        print(f"=== {name} pages={len(d)} ===")
        # sample text from page 5
        for pg in [3, 5, 8]:
            if pg < len(d):
                t = d[pg].get_text().strip()
                print(f"  -- page {pg+1} (len {len(t)}): {t[:180]!r}")
        print()
    except Exception as e:
        print(name, "ERR", e)
