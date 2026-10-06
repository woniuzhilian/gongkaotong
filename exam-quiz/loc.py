# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
LAB=re.compile(r'^[（(]\s*[A-D]\s*[）)]$')
def labels(pg):
    ws=pg.get_text("words")
    ls=[(w[4].strip('（）()'),round(w[0]),round(w[1]),round(w[2]),round(w[3])) for w in ws if LAB.match(w[4])]
    return sorted(ls,key=lambda t:(t[2],t[1]))
# distinctive stem substrings -> (id, search)
TARG={
 306:"简支梁AB 的剪力图和弯矩图如图示",
 448:"已知数字信号A 和数字信号B 的波形如图所示，则数字信号F = A + B",
 546:"图示圆轴固定端最上缘A点单元体",
 568:"已知数字信号A和数字信号B的波形如图所示,则数字信号F",
 658:"图示四种材料的应力一应变曲线中",
 666:"梁的正确挠曲线是图示四条曲线中的",
 669:"其中具有最大临界载荷",
 693:"能够完成加法运算的电路",
 784:"发生最大弯曲正应力的截面是",
 904:"图示梁的正确挠曲线大致形状",
 908:"图示四根细长压杆的抗弯刚度EI相同",
 932:"当输入电压u =1V",
 1040:"下图中电路的等效电路为",
 1050:"则数字信号F =A B+AB",
 1053:"当输入电压$u =1$V",
 1262:"其中图形关于坐标轴X、y 的静矩",
 1292:"该电路的小信号模型为",
}
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\loc.txt","w",encoding="utf-8")
for qid,stem in TARG.items():
    hits=[]
    for i in range(len(pub)):
        t=pub[i].get_text()
        if stem in t: hits.append(i+1)
    OUT.write(f"\n#### id{qid} stem={stem!r} pages={hits}\n")
    for p in hits[:2]:
        OUT.write(f"   p{p} labels: {labels(pub[p-1])}\n")
        if p<len(pub):
            OUT.write(f"   p{p+1} labels: {labels(pub[p])}\n")
OUT.close(); print(open(r"C:\Users\Administrator\.qclaw\workspace\loc.txt",encoding='utf-8').read())
