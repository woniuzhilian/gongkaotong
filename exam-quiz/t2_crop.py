# 抽样目检: 把指定 id 的命中点从原卷裁出局部, 纵向拼成一张对照表
import json, os, sys
import pymupdf
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(ROOT, '_t2_verdicts.json'), encoding='utf-8'))
BOOK = {
    u'公共基础分类版真题详解（13~24）_题目.pdf': u'题目和答案pdf/公共基础分类版真题详解（13~24）_题目.pdf',
    u'公共基础分类版真题详解（13~24）_答案解析.pdf': u'题目和答案pdf/公共基础分类版真题详解（13~24）_答案解析.pdf',
}
want = [int(a) for a in sys.argv[1:]]
tiles = []
for x in V:
    if want and x['id'] not in want:
        continue
    if not x.get('sample'):
        continue
    sm = x['sample'][0]
    if 'bbox' not in sm:
        continue
    tag = '%d-%s-%s%s' % (x['id'], x['f'], x['letter'], x['digits'])
    path = BOOK.get(x['path'])
    if not path:
        continue
    d = pymupdf.open(os.path.join(ROOT, path))
    pg = d[sm['page']]
    x0, y0, x1, y1 = sm['bbox']
    r = fitz_rect = pymupdf.Rect(max(0, x0 - 46), max(0, y0 - 13), min(pg.rect.width, x1 + 46),
                                 min(pg.rect.height, y1 + 9))
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(5.0, 5.0), clip=r)
    img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    tiles.append((tag + ' ' + x['v'] + ' sc=' + str(x.get('score')) + ' dy=' + str(sm['dy']), img))
    if len(tiles) >= 14:
        break

if not tiles:
    print('no tiles'); sys.exit(0)
W = max(t[1].width for t in tiles)
H = sum(t[1].height + 26 for t in tiles)
sheet = Image.new('RGB', (W, H), 'white')
dr = ImageDraw.Draw(sheet)
y = 0
for label, img in tiles:
    dr.text((4, y + 8), label, fill='red')
    y += 26
    sheet.paste(img, (0, y))
    y += img.height
out = os.path.join(ROOT, '_t2_crop.png')
sheet.save(out)
print('tiles=%d %s' % (len(tiles), out))
