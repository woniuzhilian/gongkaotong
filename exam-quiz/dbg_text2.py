import pymupdf, io
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
doc=pymupdf.open(PUBQ)
out=[]
for p in [146,149,165,150,151,163,200,231,232,242,243,244,245,158,202,130,223,224,127]:
    t=doc[p].get_text()
    out.append("===== PAGE %d (len %d) =====" % (p,len(t)))
    out.append(t)
doc.close()
io.open(r"C:\Users\Administrator\.qclaw\workspace\rawpages.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
