import pymupdf, os
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
OUT=r"C:\Users\Administrator\.qclaw\workspace\pgs"
doc=pymupdf.open(PUBQ)
for p in [127,146,147,150,151,152,153,158,159,162,200,201,202,203,213,223,242,243]:
    if p<doc.page_count:
        doc[p].get_pixmap(dpi=170).save(os.path.join(OUT,"pub_p%03d.png"%p))
doc.close(); print("ok")
