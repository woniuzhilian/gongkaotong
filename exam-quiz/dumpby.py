# -*- coding: utf-8 -*-
import sys, os, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
O=r"C:\Users\Administrator\.qclaw\workspace\pdftxt"
files={
 "y2022":"公共基础真题+2022.pdf",
 "y2022b":"公共基础真题+2022（补考）.pdf",
 "y2022bA":"公共基础真题解析+2022（补考）.pdf",
 "pro2024":"岩土专业基础历年真题解析册（2024版）.pdf",
 "pro2024Q":"岩土专业基础历年真题试题册（2024版）.pdf",
 "pro2024ans":"2024年注册勘察设计岩土专业基础真题答案.pdf",
}
for k,f in files.items():
    doc=pymupdf.open(os.path.join(D,f))
    out=open(os.path.join(O,k+".txt"),"w",encoding="utf-8")
    tot=0
    for i in range(len(doc)):
        t=doc[i].get_text("text"); tot+=len(t.strip())
        out.write(f"\n===== PAGE {i+1} =====\n"+t)
    out.close(); print(k,len(doc),"chars",tot)
