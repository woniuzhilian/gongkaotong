# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
files=["岩土专业基础历年真题解析册（2024版）.pdf","2024注册勘察设计岩土专业基础真题答案.pdf"]
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\pro2024.txt","w",encoding="utf-8")
for f in files:
    p=os.path.join(D,f)
    if not os.path.exists(p): OUT.write(f"MISSING {f}\n"); continue
    d=pymupdf.open(p)
    OUT.write(f"\n########## {f} pages={len(d)}\n")
    for i in range(len(d)):
        t=d[i].get_text()
        if any(k in t for k in ("地球椭球","自动安平","多跨梁","大地水准面","铅垂线","水准管","视差")):
            OUT.write(f"\n--- p{i+1} ---\n"+re.sub(r'[ \t]+',' ',t)[:1600]+"\n")
OUT.close(); print("done")
