import pymupdf, io
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
doc=pymupdf.open(PUBQ)
for p in [146,149]:
    t=doc[p].get_text()
    print("PAGE",p,"len",len(t))
    print(repr(t[:1500]))
    print("-"*60)
doc.close()
