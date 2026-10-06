# -*- coding: utf-8 -*-
import re, os, sys
sys.stdout.reconfigure(encoding="utf-8")
O=r"C:\Users\Administrator\.qclaw\workspace\pdftxt"
def pages(fn):
    txt=open(os.path.join(O,fn),encoding="utf-8").read()
    return re.split(r"\n===== PAGE (\d+) =====\n",txt)
def find(fn, pats, ctx=420):
    ps=pages(fn)
    for i in range(1,len(ps),2):
        b=ps[i+1]
        for p in pats:
            if p in b:
                idx=b.find(p)
                print(f"[{fn} p{ps[i]}] pat={p}")
                print("   "+b[max(0,idx-120):idx+ctx].replace("\n"," "))
for p in ["2022补","静矩","等效电流源","最大切应力","多跨梁","整体稳定"]:
    find("pubQ.txt",[p])
print("============ PRO ============")
for p in ["多跨梁","2018-29","工形截面","静矩","碳素结构钢","质量等级"]:
    find("pro2024Q.txt",[p])
    find("proQ.txt",[p])
