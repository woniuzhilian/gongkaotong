# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
PAGES=[143,144,147,148,150,151,152,153,158,159,162,163,164,166,167,168,201,202,203,214,215,217,218,219,220,221,222,224,225,226,227,232,233,243,244,245,246,247]
out=open(r"C:\Users\Administrator\.qclaw\workspace\selectpages.txt","w",encoding="utf-8")
for p in PAGES:
    out.write(f"\n\n========== PAGE {p} ==========\n")
    out.write(pub[p-1].get_text("text"))
out.close(); print("done")
