# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\struct.txt","w",encoding="utf-8")
PAGES=[147,148,151,152,153,166,167,168,143,144,201,202,243,244,246,247]
for p in PAGES:
    pg=pub[p-1]
    OUT.write(f"\n=================== PAGE {p} rect={pg.rect}\n")
    gi=pg.get_images(full=True)
    for g in gi:
        for r in pg.get_image_rects(g[0]):
            OUT.write(f"  IMG xref{g[0]} ({r.x0:.0f},{r.y0:.0f},{r.x1:.0f},{r.y1:.0f})\n")
    ws=pg.get_text("words")
    OUT.write("  --- words (y-sorted) ---\n")
    for w in sorted(ws,key=lambda w:(round(w[1]/3),w[0])):
        OUT.write(f"    y={w[1]:.0f} x={w[0]:.0f}-{w[2]:.0f} {w[4]!r}\n")
OUT.close(); print("done")
