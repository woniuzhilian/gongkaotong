# -*- coding: utf-8 -*-
"""打印专业基础解析册指定页的块布局，并按需裁图"""
import os, sys, io
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(ROOT, '题目和答案pdf', '岩土专业基础历年真题解析册（2024版）.pdf')
doc = pymupdf.open(PDF)
out = io.open(os.path.join(ROOT, '_pro_blocks.txt'), 'w', encoding='utf-8')
for pno in [43, 58, 59, 123, 128]:
    pg = doc[pno]
    out.write('==== p%d rect=%s\n' % (pno, pg.rect))
    bs = [b for b in pg.get_text('blocks') if b[4].strip()]
    bs.sort(key=lambda b: (b[1], b[0]))
    for b in bs:
        out.write('  y=%6.1f..%6.1f x=%5.1f..%5.1f | %s\n' % (b[1], b[3], b[0], b[2],
                b[4].replace('\n', ' ')[:110]))
out.close()

CROPS = [(1467, 59, 150, 300), (1524, 43, 90, 260), (1583, 58, 250, 420),
         (1827, 123, 262, 375), (1844, 128, 130, 230)]
for tid, pno, y0, y1 in CROPS:
    pg = doc[pno]
    r = pymupdf.Rect(60, y0, pg.rect.width - 40, y1)
    pix = pg.get_pixmap(clip=r, dpi=350)
    fn = os.path.join(ROOT, '_a', 'pro%04d.png' % tid)
    pix.save(fn)
    print(tid, fn, pix.width, pix.height)
