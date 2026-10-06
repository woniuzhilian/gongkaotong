# -*- coding: utf-8 -*-
"""专业基础两本解析册：书签目录 + 文本层可用性"""
import os, io
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
out = io.open(os.path.join(ROOT, '_pro_toc.txt'), 'w', encoding='utf-8')
for fn in ['岩土专业基础分类真题解析（16~24）_答案解析.pdf', '岩土专业基础历年真题解析册（2024版）.pdf']:
    doc = pymupdf.open(os.path.join(P, fn))
    out.write('==== %s pages=%d toc=%d\n' % (fn, doc.page_count, len(doc.get_toc())))
    txtlen = sum(len(doc[i].get_text().strip()) for i in range(min(doc.page_count, 40)))
    out.write('前40页可提取字符数=%d\n' % txtlen)
    for lvl, title, page in doc.get_toc():
        out.write('  %s%s -> p%d\n' % ('  ' * (lvl - 1), title, page))
    out.write('\n')
out.close()
print('ok')
