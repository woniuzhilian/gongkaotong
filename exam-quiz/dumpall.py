# -*- coding: utf-8 -*-
import sys, os, pymupdf
D=r"E:\应用程序开发\刷题\题目和答案pdf"
O=r"C:\Users\Administrator\.qclaw\workspace\pdftxt"; os.makedirs(O,exist_ok=True)
files={
 "pubQ":"公共基础分类版真题详解（13~24）_题目.pdf",
 "pubA":"公共基础分类版真题详解（13~24）_答案解析.pdf",
 "proQ":"岩土专业基础分类真题解析（16~24）_题目.pdf",
 "proA":"岩土专业基础分类真题解析（16~24）_答案解析.pdf",
}
for k,f in files.items():
    doc=pymupdf.open(os.path.join(D,f))
    out=open(os.path.join(O,k+".txt"),"w",encoding="utf-8")
    for i in range(len(doc)):
        out.write(f"\n===== PAGE {i+1} =====\n")
        out.write(doc[i].get_text("text"))
    out.close()
    print(k,len(doc))
