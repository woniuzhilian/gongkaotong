import os, pymupdf
ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf', '公共基础分类版真题详解（13~24）_答案解析.pdf')
OUTD = os.path.join(ROOT, '_a')
doc = pymupdf.open(P)
pg = doc[56]
pix = pg.get_pixmap(clip=pymupdf.Rect(55, 740, pg.rect.x1 - 15, pg.rect.y1), dpi=200)
pix.save(os.path.join(OUTD, 'a1344_2024_25.png'))
print('a1344_2024_25.png', pix.width, pix.height)
pg = doc[57]
nb = [b for b in pg.get_text('blocks') if b[4].strip()]
ys = [b[1] for b in nb if '2024-26' in b[4]]
y1 = ys[0] if ys else pg.rect.y1
pix = pg.get_pixmap(clip=pymupdf.Rect(55, 0, pg.rect.x1 - 15, y1 - 3), dpi=200)
pix.save(os.path.join(OUTD, 'a1344_2024_25_b.png'))
print('a1344_2024_25_b.png', pix.width, pix.height)
