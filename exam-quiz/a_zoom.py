import os, pymupdf
ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf', '公共基础分类版真题详解（13~24）_答案解析.pdf')
doc = pymupdf.open(P)
pg = doc[89]
pix = pg.get_pixmap(clip=pymupdf.Rect(150, 136, 430, 170), dpi=600)
pix.save(os.path.join(ROOT, '_a', 'zoom1122.png'))
print('crop %dx%d' % (pix.width, pix.height))
