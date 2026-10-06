# -*- coding: utf-8 -*-
"""2023-15 解析行的字符级排布，判定指数 n 属于分母还是整个分式"""
import os, io
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(ROOT, '题目和答案pdf', '公共基础分类版真题详解（13~24）_答案解析.pdf')
doc = pymupdf.open(PDF)
pno = 0
for i in range(len(doc)):
    if '【2023-15】' in doc[i].get_text():
        pno = i
        break
pg = doc[pno]
blocks = [b for b in pg.get_text('rawdict')['blocks'] if b.get('type') == 0]
blocks.sort(key=lambda b: b['bbox'][1])
start = 0
for i, b in enumerate(blocks):
    t = ''.join(c['c'] for l in b['lines'] for s in l['spans'] for c in s['chars'])
    if '2023-15' in t:
        start = i
        break
out = io.open(os.path.join(ROOT, '_r1214.txt'), 'w', encoding='utf-8')
out.write('page(0-based)=%d\n' % pno)
for b in blocks[start:start + 9]:
    out.write('--- block y=%s\n' % round(b['bbox'][1], 1))
    for l in b['lines']:
        seq = []
        for s in l['spans']:
            for c in s['chars']:
                seq.append((c['c'], round(c['bbox'][0], 1), round(c['bbox'][1], 1),
                            round(c['bbox'][3], 1), round(s['size'], 1), s['font']))
        out.write('LINE: %s\n' % ''.join(x[0] for x in seq))
        for ch, x0, y0, y1, sz, fn in seq:
            out.write('   %r x=%s ytop=%s ybot=%s sz=%s %s\n' % (ch, x0, y0, y1, sz, fn))
out.close()
print('ok')
