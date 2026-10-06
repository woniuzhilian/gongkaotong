import os, json, pymupdf
ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf', '公共基础分类版真题详解（13~24）_答案解析.pdf')
doc = pymupdf.open(P)
pg = doc[89]
d = pg.get_text('rawdict', clip=pymupdf.Rect(150, 134, 435, 172))
out = []
for bl in d['blocks']:
    for ln in bl.get('lines', []):
        for sp in ln['spans']:
            chars = ''.join(c['c'] for c in sp['chars'])
            cps = ' '.join('U+%04X' % ord(c['c']) for c in sp['chars'])
            out.append('font=%s size=%.1f color=%s text=%r' % (sp['font'], sp['size'], sp['color'], chars))
            out.append('    codes: %s' % cps)
# 对照：同页 2023-43 的正常 ⊖
d2 = pg.get_text('rawdict', clip=pymupdf.Rect(150, 236, 420, 270))
out.append('--- 对照 2023-43 公式行 ---')
for bl in d2['blocks']:
    for ln in bl.get('lines', []):
        for sp in ln['spans']:
            chars = ''.join(c['c'] for c in sp['chars'])
            out.append('font=%s text=%r' % (sp['font'], chars))
            out.append('    codes: %s' % ' '.join('U+%04X' % ord(c['c']) for c in sp['chars']))
open(os.path.join(ROOT, '_a_1122b.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
