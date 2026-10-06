import pymupdf, os
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
OUT=r"C:\Users\Administrator\.qclaw\workspace\pgs"
doc=pymupdf.open(PUBQ)
for p in [142,143,144,163,164,165,166,217,218,219,220,221,222,225,226,241,244,245,246,247,35,36,41,42,87,88,89]:
    if p<doc.page_count:
        doc[p].get_pixmap(dpi=170).save(os.path.join(OUT,"pub_p%03d.png"%p))
doc.close()
print("ok")
