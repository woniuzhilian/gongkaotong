# -*- coding: utf-8 -*-
import io, re, os
import pymupdf

BASE = r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ = os.path.join(BASE, "公共基础分类版真题详解（13~24）_题目.pdf")
PROQ = os.path.join(BASE, "岩土专业基础分类真题解析（16~24）_题目.pdf")

# id -> (which_pdf, marker as it appears)
MAP = {
 306:("pub","【2016-67】"),
 448:("pub","【2017-89】"),
 546:("pub","【2018-67】"),
 568:("pub","【2018-89】"),
 658:("pub","【2019-59】"),
 666:("pub","【2019-67】"),
 669:("pub","【2019-70】"),
 693:("pub","【2019-94】"),
 784:("pub","【2020-65】"),
 813:("pub","【2020-94】"),
 904:("pub","【2021-65】"),
 908:("pub","【2021-69】"),
 928:("pub","【2021-90】"),
 932:("pub","【2021-93】"),
 1040:("pub","【2022-81】"),
 1050:("pub","【2022-91】"),
 1053:("pub","【2022-94】"),
 1147:("pub","【2022补-68】"),
 1160:("pub","【2022补-81】"),
 1262:("pub","【2023-63】"),
 1292:("pub","【2023-93】"),
 1588:("pro","2018"),
 2002:("pro","2024"),
}

def norm(s): return re.sub(r"\s+","",s)

out=[]
for qid,(kind,marker) in MAP.items():
    path = PUBQ if kind=="pub" else PROQ
    doc = pymupdf.open(path)
    pages=[]
    for p in range(doc.page_count):
        t=norm(doc[p].get_text())
        if norm(marker) in t:
            pages.append(p)
    out.append("id=%s kind=%s marker=%s pages=%s"%(qid,kind,marker,pages))
    doc.close()
io.open(r"C:\Users\Administrator\.qclaw\workspace\marker_pages.txt","w",encoding="utf-8").write("\n".join(out))
print("done")
