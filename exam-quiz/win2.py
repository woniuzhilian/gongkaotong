# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
pro=pymupdf.open(os.path.join(D,"岩土专业基础历年真题试题册（2024版）.pdf"))
def ctx(doc,anchor,before=0,after=300):
    for i in range(len(doc)):
        t=doc[i].get_text()
        for m in re.finditer(re.escape(anchor),t):
            return i+1, re.sub(r'[ \t]+',' ',t[max(0,m.start()-before):m.start()+after])
    return None,None
TASKS=[
 (pub,"【2017-94】",0,360),
 (pub,"采用两种方案均可",700,120),
 (pub,"任选3个KCL方程和2个KVL方程",900,120),
 (pub,"【2019-96】",0,320),
 (pub,"【2019-83】",0,320),
 (pub,"【2021-1】",0,300),
 (pub,"【2013-95】",0,360),
 (pub,"复位信号R",0,200),
 (pub,"D触发器",0,260),
]
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\win2.txt","w",encoding="utf-8")
for doc,anchor,b,a in TASKS:
    pg,w=ctx(doc,anchor,b,a)
    OUT.write(f"\n===== anchor={anchor!r} p{pg}\n  {w}\n")
OUT.close(); print("done")
