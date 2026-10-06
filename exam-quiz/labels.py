# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\labels.txt","w",encoding="utf-8")
PAGES=[147,214,218,150,166,151,152,167,143,246,245,201,225,227,128,163,164,232,221,222,214,196,197,167,168,159,203,204,246]
for p in PAGES:
    pg=pub[p-1]
    ws=pg.get_text("words")
    labs=[w for w in ws if re.fullmatch(r'[（(]\s*[A-Da-d]\s*[）)]', w[4])]
    if not labs: 
        OUT.write(f"\n### p{p}: no label-words; text_with_parens={[w[4] for w in ws if re.search(r'[（(][A-D][）)]',w[4])][:20]}\n")
        continue
    OUT.write(f"\n### p{p}\n")
    for w in sorted(labs,key=lambda w:(round(w[1]),w[0])):
        OUT.write(f"  {w[4]!r} x0={w[0]:.0f} y0={w[1]:.0f} x1={w[2]:.0f} y1={w[3]:.0f}\n")
OUT.close(); print(open(r"C:\Users\Administrator\.qclaw\workspace\labels.txt",encoding='utf-8').read())
