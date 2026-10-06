# -*- coding: utf-8 -*-
"""Crop option sub-figures for broken questions. fitz coords, 0-based page idx."""
import os, pymupdf
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ=BASE+r"\公共基础分类版真题解析（16~24）_题目.pdf"
PUBQ=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
OUT=r"C:\Users\Administrator\.qclaw\workspace\crops_v2"
os.makedirs(OUT,exist_ok=True)

# (id, letter, page0, (x0,y0,x1,y1))
CROPS = [
 (306,"A",146,(88,647,243,709)),(306,"B",146,(323,647,471,709)),
 (306,"C",147,(88,76,229,141)),(306,"D",147,(325,76,474,145)),
 (658,"stem",127,(180,436,414,534)),
 (784,"A",151,(104,563,184,643)),(784,"B",151,(205,563,280,643)),
 (784,"C",151,(307,563,381,643)),(784,"D",151,(408,563,488,643)),
 (908,"A",166,(378,396,439,587)),(908,"B",166,(156,405,217,598)),
 (908,"C",166,(237,405,297,586)),(908,"D",166,(307,408,368,587)),
 (904,"A",152,(153,183,319,220)),(904,"B",152,(366,182,457,222)),
 (904,"C",152,(153,240,272,268)),(904,"D",152,(366,240,457,268)),
]
doc=pymupdf.open(PUBQ)
for qid,letter,pg,bb in CROPS:
    p=doc[pg]
    clip=pymupdf.Rect(*bb)
    pix=p.get_pixmap(dpi=200,clip=clip)
    fn="q%d_%s_p%d.png"%(qid,letter,pg)
    pix.save(os.path.join(OUT,fn))
    print(fn,pix.width,pix.height)
doc.close()
