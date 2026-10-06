# -*- coding: utf-8 -*-
import sys, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')
PUB=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
PRO=r"E:\应用程序开发\刷题\题目和答案pdf\岩土专业基础分类真题解析（16~24）_题目.pdf"
dub=pymupdf.open(PUB)
def dump(path):
    return pymupdf.open(path)
dpro=None
try: dpro=dump(PRO)
except Exception as e: print("pro open fail",e)

anchors={
306:"剪力图和弯矩图如图示",447:"AC+DC+ADC",448:"数字信号F=A+B的波形",538:"变截面杆",
546:"最上缘A点单元体",568:"数字信号F=A+B的波形图",658:"四种材料的应力",666:"正确挠曲线是图示四条曲线",
669:"四根细长",693:"能够完成加法运算",784:"整块材料",813:"运算放大器输出电压的极限值",
904:"挠曲线大致形状",908:"抗弯刚度EI相同",928:"ABC+AD+BD+CD",932:"输出电压波形",
1040:"等效电路为",1050:"的波形",1053:"输出电压波形",1147:"平面应力状态",1160:"等效电流源模型",
1262:"静矩",1292:"小信号模型",1588:"工形截面简支梁",1626:"质量等级最高",2002:"多跨梁的弯矩图",
}
def locate(doc, sub):
    hits=[]
    for i in range(len(doc)):
        t=doc[i].get_text()
        if sub in t:
            # nearest preceding 【year-num】
            pos=t.find(sub)
            pre=list(re.finditer(r'【([^】]*?)】', t[:pos]))
            mk=pre[-1].group(1) if pre else None
            hits.append((i+1,mk))
    return hits
for qid,sub in anchors.items():
    hp=locate(dub, sub) if dub else []
    hpr=locate(dpro, sub) if dpro else []
    print(f"id{qid} :: PUB {hp} | PRO {hpr}")
