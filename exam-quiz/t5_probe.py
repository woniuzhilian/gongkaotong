# -*- coding: utf-8 -*-
"""验证假设：原书里 + - 这些符号用的是哪个字体、PyMuPDF 抽出来是什么字符"""
import os, re, io, json
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
BOOKS = [
    ('答案', os.path.join(ROOT, '题目和答案pdf', '公共基础分类版真题详解（13~24）_答案解析.pdf')),
    ('题目', os.path.join(ROOT, '题目和答案pdf', '公共基础分类版真题详解（13~24）_题目.pdf')),
]
PROBES = json.load(io.open(os.path.join(ROOT, '_t5_probe.json'), encoding='utf-8'))
OUT = io.open(os.path.join(ROOT, '_t5_probe.txt'), 'w', encoding='utf-8', newline='\r\n')

for tag, path in BOOKS:
    if not os.path.exists(path):
        OUT.write('缺文件 %s\n' % path)
        continue
    d = pymupdf.open(path)
    for probe in PROBES:
        for pno in range(len(d)):
            rects = d[pno].search_for(probe)
            if not rects:
                continue
            r = rects[0]
            clip = pymupdf.Rect(max(0, r.x0 - 10), max(0, r.y0 - 30),
                                min(d[pno].rect.x1, r.x1 + 260), min(d[pno].rect.y1, r.y1 + 150))
            OUT.write('\n== [%s] p%d 探针「%s」\n' % (tag, pno, probe))
            rd = d[pno].get_text('rawdict', clip=clip)
            for bl in rd['blocks'][:6]:
                for ln in bl.get('lines', [])[:14]:
                    desc = []
                    for sp in ln['spans'][:40]:
                        txt = ''.join(ch['c'] for ch in sp['chars'])
                        desc.append('<%s|%s>%s' % (sp['font'], round(sp['size'], 1), txt))
                    OUT.write('   ' + ' '.join(desc)[:1500] + '\n')
            break
    d.close()
OUT.write('\nDONE\n')
OUT.close()
print('ok')
