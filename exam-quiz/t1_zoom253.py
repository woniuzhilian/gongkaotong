import pymupdf, os

PDF = os.path.join('题目和答案pdf', '公共基础分类版真题详解（13~24）_题目.pdf')
doc = pymupdf.open(PDF)
pg = doc[22]
out = []
for b in pg.get_text('blocks'):
    if 530 < b[1] < 640:
        out.append('x0=%.1f y0=%.1f x1=%.1f y1=%.1f %r' % (b[0], b[1], b[2], b[3], b[4]))
pm = pg.get_pixmap(clip=pymupdf.Rect(183, 578, 260, 618), dpi=700)
pm.save('_t1/zoom253d.png')
out.append('crop=%dx%d' % (pm.width, pm.height))
open('_z2.txt', 'w', encoding='utf-8').write('\n'.join(out))
