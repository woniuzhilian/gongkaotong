# -*- coding: utf-8 -*-
import re, os, sys
sys.stdout.reconfigure(encoding="utf-8")
O=r"C:\Users\Administrator\.qclaw\workspace\pdftxt"
def show(fn, pats, ctx=600):
    txt=open(os.path.join(O,fn),encoding="utf-8").read()
    pages=re.split(r"\n===== PAGE (\d+) =====\n",txt)
    for i in range(1,len(pages),2):
        body=pages[i+1]
        for p in pats:
            if p in body:
                print(f"--- {fn} p{pages[i]} pat={p} ---")
                idx=body.find(p)
                print(body[max(0,idx-200):idx+ctx].replace("\n"," "))
                print()
show("y2022.txt",["等效电路","A B+AB","�B+AB","输出电压波形","运算放大器"])
print("======= pro2024Q =======")
show("pro2024Q.txt",["多跨梁","弯矩图大致形状","质量等级","碳素结构钢"])
