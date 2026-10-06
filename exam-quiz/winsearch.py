# -*- coding: utf-8 -*-
"""Print a text window around a fragment in a chosen PDF, to recover truncated stems."""
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
PDFDIR=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_题目.pdf")
PRO=os.path.join(PDFDIR,"岩土专业基础历年真题试题册（2024版）.pdf")
PUBANS=os.path.join(PDFDIR,"公共基础分类版真题详解（13~24）_答案解析.pdf")
DOCS={"pub":pymupdf.open(PUB),"pro":pymupdf.open(PRO),"pubans":pymupdf.open(PUBANS)}
def find(doc,frag,n=520):
    hits=[]
    for i in range(len(doc)):
        t=doc[i].get_text()
        for m in re.finditer(re.escape(frag),t):
            hits.append((i+1, re.sub(r'[ \t]+',' ',t[max(0,m.start()-120):m.start()+n])))
    return hits
TASKS=[
 ("682","pub","额定容量为"),
 ("1151","pub","任一封闭曲线的速度环量"),
 ("1155","pub","平坡棱柱形渠道"),
 ("1218","pub","且其秩"),
 ("1391","pub","动量方程"),
 ("94","pub","从时钟信号CP的第一上升沿"),
 ("451","pub","频率发生改变"),
 ("560","pub","任选3个KCL方程"),
 ("561","pub","采用两种方案均可"),
 ("695","pub","右移寄存器"),
 ("840","pub","lim"),
 ("1680","pro","玻璃态物质"),
 ("1932","pro","详细勘察是为了"),
 ("1888","pro","全预应力混凝土"),
 ("1987","pro","地球椭球"),
 ("1988","pro","自动安平水准仪"),
 ("2002","pro","图示多跨梁的弯矩图"),
]
seen=set()
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\ws_out.txt","w",encoding="utf-8")
for qid,src,frag in TASKS:
    OUT.write(f"\n=============== id{qid} [{src}] frag={frag}\n")
    for pg,win in find(DOCS[src],frag)[:6]:
        OUT.write(f"  -- p{pg}: {win}\n")
OUT.close()
print("done")
