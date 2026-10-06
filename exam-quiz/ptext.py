# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
PAGES=[128,143,144,147,148,150,151,152,153,163,164,166,167,168,201,202,214,215,219,221,222,224,225,243,244,245,246,247]
for p in PAGES:
    t=pub[p-1].get_text()
    print(f"\n========== p{p} ==========")
    print(t.strip())
