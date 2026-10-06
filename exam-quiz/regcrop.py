# -*- coding: utf-8 -*-
import sys, os, pymupdf
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBS={"pub":BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf",
      "pro":BASE+r"\岩土专业基础分类真题解析（16~24）_题目.pdf"}
OUT=r"C:\Users\Administrator\.qclaw\workspace\vreg"
os.makedirs(OUT,exist_ok=True)
# args: kind page x0 y0 x1 y1 name
k,p,x0,y0,x1,y1,name=sys.argv[1],int(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6]),sys.argv[7]
doc=pymupdf.open(PUBS[k])
pix=doc[p].get_pixmap(dpi=170,clip=pymupdf.Rect(x0,y0,x1,y1))
pix.save(os.path.join(OUT,name+".png"))
print(name,pix.width,pix.height)
doc.close()
