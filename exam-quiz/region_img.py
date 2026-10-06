# -*- coding: utf-8 -*-
"""Render the full question block (stem+options) from a PDF into one PNG per question."""
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
OUT=r"C:\Users\Administrator\.qclaw\workspace\qblocks"
os.makedirs(OUT, exist_ok=True)
PUB=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
PRO=r"E:\应用程序开发\刷题\题目和答案pdf\岩土专业基础历年真题试题册（2024版）.pdf"
QN=re.compile(r'【\d{4}(?:\s?补)?[-\u2013]\d+】')

def norm(s):
    s=re.sub(r'<[^>]+>','',str(s)); s=re.sub(r'\$[^$]*\$','',s)
    return re.sub(r'[^\u4e00-\u9fff0-9A-Za-z]','',s)
def find(doc, sub):
    ns=norm(sub)
    for i in range(len(doc)):
        t=doc[i].get_text()
        if sub in t or (ns and ns in norm(t)): return i
    return None

def render_block(doc, i, sub, name, dpi=170, pad=4):
    page=doc[i]
    words=page.get_text("words")
    # bounding boxes of words after stem start on this page
    ys=[w[1] for w in words if sub[:8] in w[4]] or [w[1] for w in words]
    y0=min(ys)-6
    # extend to bottom of page (options may follow)
    clip=pymupdf.Rect(20, y0, page.rect.x1-20, page.rect.y1-20)
    pix=page.get_pixmap(clip=clip, dpi=dpi)
    fn=os.path.join(OUT,name+".png"); pix.save(fn)
    return fn

if __name__=="__main__":
    dub=pymupdf.open(PUB); dpro=pymupdf.open(PRO)
    jobs=[
      (306,"简支梁AB的剪力图",dub),(447,"AC+DC+ADC",dub),(448,"数字信号F=A+B的波形",dub),
      (538,"变截面杆 AC",dub),(546,"最上缘A点单元体",dub),(568,"数字信号F=A+B",dub),
      (666,"筒支梁受力如图",dub),(669,"四根细长",dub),(693,"能够完成加法运算",dub),
      (784,"整块材料",dub),(813,"运算放大器输出电压的极限值",dub),(904,"挠曲线大致形状",dub),
      (908,"抗弯刚度EI相同",dub),(928,"ABC+AD+BD+CD",dub),(932,"输出电压波形为",dub),
      (1040,"等效电路为",dub),(1050,"数字信号$F =A B+AB$",dub),(1053,"输出电压波形",dub),
      (1147,"平面应力状态",dub),(1160,"等效电流源模型",dub),(1262,"静矩",dub),(1292,"小信号模型",dub),
      (1588,"工形截面简支梁的跨度",dpro),(1626,"质量等级最高的等级",dpro),(1680,"玻璃态物质",dpro),(1932,"详细勘察是为了",dpro),
    ]
    for qid,sub,doc in jobs:
        i=find(doc,sub)
        if i is None: print(f"id{qid} NOTFOUND"); continue
        f=render_block(doc,i,sub,f"q{qid}_p{i+1}")
        print(f"id{qid} page{i+1} -> {os.path.basename(f)}")
