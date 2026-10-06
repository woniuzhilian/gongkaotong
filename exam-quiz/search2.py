# -*- coding: utf-8 -*-
import io, sys, re, os
import pymupdf

BASE = r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ = os.path.join(BASE, "公共基础分类版真题详解（13~24）_题目.pdf")
PUBA = os.path.join(BASE, "公共基础分类版真题详解（13~24）_答案解析.pdf")
PROQ = os.path.join(BASE, "岩土专业基础分类真题解析（16~24）_题目.pdf")
PROA = os.path.join(BASE, "岩土专业基础分类真题解析（16~24）_答案解析.pdf")

targets = {
 306:("pub","多跨梁"),
 448:("pub","输出逻辑"),
 546:("pub","圆轴固定端"),
 568:("pub","输出逻辑"),
 658:("pub","应力-应变曲线"),
 666:("pub","筒支梁"),
 669:("pub","临界荷载"),
 693:("pub","加法运算"),
 784:("pub","两端固定"),
 813:("pub","运算放大器"),
 904:("pub","挠曲线"),
 908:("pub","临界荷载"),
 928:("pub","最简与或"),
 932:("pub","运算放大器"),
 1040:("pub","等效电路"),
 1050:("pub","输出逻辑"),
 1053:("pub","运算放大器"),
 1147:("pub","最大剪应力"),
 1160:("pub","等效电源"),
 1262:("pub","静矩"),
 1292:("pub","小信号模型"),
 1588:("pro","矩形截面简支梁"),
 2002:("pro","多跨梁"),
}

def norm(s):
    return re.sub(r"\s+","",s)

def search(doc, kw):
    res=[]
    for pno in range(doc.page_count):
        t=doc[pno].get_text()
        if kw in norm(t):
            res.append(pno)
    return res

out=[]
for qid,(kind,kw) in targets.items():
    path = PUBQ if kind=="pub" else PROQ
    doc = pymupdf.open(path)
    pages = search(doc, kw)
    out.append("### id=%s kind=%s kw=%s -> pages %s" % (qid,kind,kw,pages))
    for p in pages[:6]:
        t=norm(doc[p].get_text())
        i=t.find(kw)
        out.append("  p%d: ...%s..." % (p, t[max(0,i-60):i+140]))
    doc.close()

io.open(r"C:\Users\Administrator\.qclaw\workspace\search_res.txt","w",encoding="utf-8").write("\n".join(out))
print("done", len(out))
