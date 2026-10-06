import os, pymupdf
ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf', '公共基础分类版真题详解（13~24）_答案解析.pdf')
OUTD = os.path.join(ROOT, '_a')
doc = pymupdf.open(P)
pg = doc[89]
out = ['page h=%.1f' % pg.rect.y1]
for b in pg.get_text('blocks'):
    if b[4].strip() and b[1] < 300:
        out.append('y0=%.1f y1=%.1f x0=%.1f %r' % (b[1], b[3], b[0], b[4][:80]))
pix = pg.get_pixmap(clip=pymupdf.Rect(55, 72, pg.rect.x1 - 15, 260), dpi=200)
pix.save(os.path.join(OUTD, 'a1122_2022补_43.png'))
out.append('crop %dx%d' % (pix.width, pix.height))
open(os.path.join(ROOT, '_a_1122.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
