# -*- coding: utf-8 -*-
import sys, os, re, glob, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
docs={}
for f in glob.glob(os.path.join(D,"*.pdf")):
    try: docs[os.path.basename(f)]=pymupdf.open(f)
    except Exception as e: docs[os.path.basename(f)]=None
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\find2.txt","w",encoding="utf-8")
QUERIES=["大地水准面是一个包围整个地球","地球椭球，地球椭球的法线","自动安平水准仪的没有管水准器","质量等级最高的等级","整体稳定性最好的是","图示多跨梁的弯矩图大致形状","强角最大的是","图示电路中,能够完成加法运算"]
for q in QUERIES:
    OUT.write(f"\n########## {q}\n")
    for name,doc in docs.items():
        if doc is None: continue
        for i in range(len(doc)):
            t=doc[i].get_text()
            if q in t:
                m=t.find(q)
                OUT.write(f"  [{name}] p{i+1}: "+re.sub(r'[ \t\n]+',' ',t[max(0,m-80):m+260])+"\n")
                break
OUT.close(); print("done")
