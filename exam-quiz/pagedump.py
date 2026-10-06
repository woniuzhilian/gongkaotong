# -*- coding: utf-8 -*-
import io, re, os
import pymupdf
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ=os.path.join(BASE,"公共基础分类版真题详解（13~24）_题目.pdf")
PROQ=os.path.join(BASE,"岩土专业基础分类真题解析（16~24）_题目.pdf")
pages=[126,127,128,129,130,131,145,146,147,148,149,150,151,152,153,157,158,159,160,161,162,163,164,165,166,199,200,201,202,203,222,223,224,225,230,231,232,233,241,242,243,244,245,246]
out=[]
doc=pymupdf.open(PUBQ)
for p in pages:
    if p>=doc.page_count: continue
    d=doc[p].get_text("dict")
    out.append("\n\n########## PUBQ 0-based page %d (1-based %d) ##########"%(p,p+1))
    for b in d["blocks"]:
        if b.get("type")!=0: continue
        for l in b["lines"]:
            txt="".join(s["text"] for s in l["spans"]).strip()
            if txt:
                y=round(l["bbox"][1],1); x=round(l["bbox"][0],1)
                out.append("  y=%7.1f x=%6.1f | %s"%(y,x,txt))
doc.close()
io.open(r"C:\Users\Administrator\.qclaw\workspace\pagedump_pub.txt","w",encoding="utf-8").write("\n".join(out))
print("done")
