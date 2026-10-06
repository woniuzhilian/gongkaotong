import pymupdf, io, re, json
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
PROQ=BASE+r"\岩土专业基础分类真题解析（16~24）_题目.pdf"
def norm(s): return re.sub(r"\s+","",s).replace("\u3000","")
KEYS={
306:"该梁正确的受力图是",448:"则数字信号F=A+B的波形为",546:"最上缘A点单元体的应力状态是",
568:"则数字信号F=A+B的波形图",658:"强度最大的材料是",666:"梁的正确挠曲线是图示四条曲线中的",
669:"其中具有最大临界载荷",693:"能够完成加法运算的电路",784:"发生最大弯曲正应力的截面是",
813:"端送入，电路的",904:"图示梁的正确挠曲线大致形状是",908:"图示四根细长压杆的抗弯刚度EI相同",
928:"对逻辑表达式ABC",932:"则电路的输出电压ui的平均值",1040:"下图中电路的等效电路为",
1050:"的波形:",1053:"当输入电压ui1=1V",1147:"具有最大切应力的是",1160:"图示电路的等效电流源模型为",
1262:"其中图形关于坐标轴X、y的静矩",1292:"该电路的小信号模型为",1588:"工形截面简支梁的跨度",
2002:"多跨梁的弯矩图大致形状正确"}
docs={"pub":pymupdf.open(PUBQ),"pro":pymupdf.open(PROQ)}
pages={k:[norm(docs[k][p].get_text()) for p in range(docs[k].page_count)] for k in docs}
out=[]
for qid,key in KEYS.items():
    nk=norm(key)
    hits=[]
    for k in ("pub","pro"):
        for p,t in enumerate(pages[k]):
            if nk in t: hits.append("%s:%d"%(k,p))
    out.append("id=%s key='%s' -> %s"%(qid,key,hits))
for k in docs: docs[k].close()
io.open(r"C:\Users\Administrator\.qclaw\workspace\textpage.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
