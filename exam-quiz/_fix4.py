"""重切最后 4 道题(id=1147/1160/1588/2002)的题干与选项配图，并写回 questions.json"""
import os, json, shutil
import pymupdf
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
OUTDIR = os.path.join(ROOT, 'exam-quiz', 'public', 'images', 'q23')
BAK = os.path.join(ROOT, '_fix_backup')
log = open(os.path.join(ROOT, '_fix4_out.txt'), 'w', encoding='utf-8')
DPI = 300


def p(*a):
    print(*a, file=log)


if not os.path.isdir(BAK):
    os.mkdir(BAK)
if not os.path.isfile(os.path.join(BAK, 'questions_BEFORE_FIX4.json')):
    shutil.copy(DB, os.path.join(BAK, 'questions_BEFORE_FIX4.json'))

DOCS = {
    'pub': '公共基础分类版真题详解（13~24）_题目.pdf',
    'pro35': '岩土专业基础历年真题试题册（2024版）.pdf',
    'procls': '岩土专业基础分类真题解析（16~24）_题目.pdf',
}
docs = {k: pymupdf.open(os.path.join(P, v)) for k, v in DOCS.items()}


def trim(im, pad=10, thr=232):
    """裁掉四周空白，保留 pad 像素边距"""
    g = im.convert('L').point(lambda v: 255 if v < thr else 0)
    bb = g.getbbox()
    if not bb:
        return im
    x0 = max(0, bb[0] - pad)
    y0 = max(0, bb[1] - pad)
    x1 = min(im.width, bb[2] + pad)
    y1 = min(im.height, bb[3] + pad)
    return im.crop((x0, y0, x1, y1))


def crop(key, pno, x0, y0, x1, y1, name, do_trim=True):
    pix = docs[key][pno].get_pixmap(clip=pymupdf.Rect(x0, y0, x1, y1), dpi=DPI)
    fp = os.path.join(OUTDIR, name)
    if do_trim:
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        im = trim(im)
        im.save(fp)
        w, h = im.size
    else:
        pix.save(fp)
        w, h = pix.width, pix.height
    p('  %-22s %dx%d  <- %s p%d (%.0f,%.0f,%.0f,%.0f)' % (name, w, h, key, pno, x0, y0, x1, y1))
    return '/images/q23/' + name


def tag(rel):
    return '<img src="%s" style="max-width:100%%;" />' % rel


# 1 px = 1/ (DPI/72) pt ; 下面坐标统一用 pt
S = DPI / 72.0


def px2pt(v, origin):
    return origin + v / S


# ---------- id=1147 : 分类版题目册 p158, 4 个应力状态图 ----------
p('=== id=1147 (2022补-68 平面应力状态最大切应力) ===')
X0, Y0 = 86.0, 398.0                      # a1147_strip 渲染原点
colb = [(0, 400), (400, 790), (790, 1222), (1222, 1901)]
rowfig = (50, 330)
r1147 = {}
for L, (a, b) in zip('ABCD', colb):
    r1147[L] = crop('pub', 158, px2pt(a, X0), px2pt(rowfig[0], Y0),
                    px2pt(b, X0), px2pt(rowfig[1], Y0), 'id1147_opt%s.png' % L)
r1147['stem'] = crop('pub', 158, 86, 400, 542, 510, 'id1147_stem.png')

# ---------- id=1160 : 分类版题目册 p202 ----------
p('\n=== id=1160 (2022补-81 等效电流源模型) ===')
s1160 = crop('pub', 202, 88, 270, 220, 345, 'id1160_stem.png')
OX, OY = 88.0, 343.0
cells = {'A': (0, 116, 421, 310), 'B': (421, 116, 855, 310),
         'C': (0, 434, 421, 629), 'D': (421, 434, 855, 629)}
o1160 = {}
for L, (a, b, c, d) in cells.items():
    o1160[L] = crop('pub', 202, px2pt(a, OX), px2pt(b, OY),
                    px2pt(c, OX), px2pt(d, OY), 'id1160_opt%s.png' % L)

# ---------- id=1588 : 试题册 p36, 4 个选项竖排 ----------
p('\n=== id=1588 (2018-29 工形截面简支梁整体稳定) ===')
PX0, PY0 = 130.0, 80.0
rows1588 = {'A': (74, 272), 'B': (374, 539), 'C': (646, 813), 'D': (937, 1135)}
o1588 = {}
for L, (a, b) in rows1588.items():
    o1588[L] = crop('pro35', 36, 130, px2pt(a, PY0), 392, px2pt(b, PY0),
                    'id1588_opt%s.png' % L)

# ---------- id=2002 : 专业基础分类版题目册 p53 (扫描页) ----------
p('\n=== id=2002 (2024-27 多跨梁弯矩图) ===')
Q0 = 200.0 / 72.0                          # a2002_p53 以 200dpi 渲染, px -> pt 需除以该比例
def px2pt200(v):
    return v / Q0
rows2002 = {'stem': (1293, 1379), 'A': (1396, 1515), 'B': (1537, 1655),
            'C': (1677, 1796), 'D': (1818, 1932)}
r2002 = {}
for L, (a, b) in rows2002.items():
    r2002[L] = crop('procls', 53, px2pt200(60), px2pt200(a), px2pt200(1620),
                    px2pt200(b), 'id2002_%s.png' % ('stem' if L == 'stem' else 'opt' + L))

# ---------- 写回 ----------
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}

q = byid[1147]
q['question'] = '图示4中平面应力状态，具有最大切应力的是：（　　）<br>' + tag(r1147['stem'])
for L in 'ABCD':
    q[L] = tag(r1147[L])

q = byid[1160]
q['question'] = '图示电路的等效电流源模型为：（　　）<br>' + tag(s1160)
for L in 'ABCD':
    q[L] = tag(o1160[L])

q = byid[1588]
q['question'] = '图中所示工形截面简支梁的跨度、截面尺寸和约束条件均相同，根据弯矩图（$|M_1| > |M_2|$）可判断整体稳定性最好的是（　　）'
for L in 'ABCD':
    q[L] = tag(o1588[L])

q = byid[2002]
q['question'] = '图示多跨梁的弯矩图大致形状正确的是（　　）<br>' + tag(r2002['stem'])
for L in 'ABCD':
    q[L] = tag(r2002[L])

json.dump(data, open(DB, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
chk = json.load(open(DB, encoding='utf-8'))
p('\n写回完成，题库共 %d 题' % len(chk))
for tid in (1147, 1160, 1588, 2002):
    z = next(x for x in chk if x['id'] == tid)
    p('  id=%-5s 答案=%s  题干含图=%s  选项空=%s' % (
        tid, z['answer'], 'src=' in (z['question'] or ''),
        [L for L in 'ABCD' if not (z[L] or '').strip()]))
for d in docs.values():
    d.close()
log.close()
print('ok')
