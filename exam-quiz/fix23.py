"""修复 #1：23 题选项不可作答。
从源 PDF 重新切出题干图/选项图，并回填 PDF 中本就存在、但 JSON 丢失的选项文字。
"""
import json, os, shutil, sys
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
PUB_Q = os.path.join(ROOT, '题目和答案pdf', '公共基础分类版真题详解（13~24）_题目.pdf')
OUTDIR = os.path.join(ROOT, 'exam-quiz', 'public', 'images', 'q23')
DPI = 300
SCALE = DPI / 72.0

os.makedirs(OUTDIR, exist_ok=True)

# 备份
if '--nobak' not in sys.argv:
    bak = os.path.join(ROOT, '_fix_backup', 'questions_BEFORE_FIX23.json')
    os.makedirs(os.path.dirname(bak), exist_ok=True)
    shutil.copy2(DB, bak)
    print('已备份 ->', bak)

data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
doc = pymupdf.open(PUB_Q)

# 规格表
# stem: (page, x0, y0, x1, y1) 或 None
# opts: 'text' -> [4 段文字]   'img' -> [(page,x0,y0,x1,y1) x4]
SPEC = {
    306: dict(stem=(146, 124, 553, 470, 645),
              opts='img', boxes=[(146, 86, 646, 245, 711), (146, 322, 646, 473, 711),
                                 (147, 86, 78, 231, 143), (147, 324, 74, 476, 147)]),
    448: dict(stem=(231, 204, 635, 415, 737),
              opts='text', texts=['$U_2(t)$出现频率失真', '$U_2(t)$的有效值$U_2=AU_1$',
                                  '$U_2(t)$的有效值$U_2<AU_1$', '$U_2(t)$的有效值$U_2>AU_1$']),
    546: dict(stem=(161, 179, 643, 414, 710),
              opts='text',
              texts=[r'$\sigma_{eq3}=\dfrac{32\sqrt{F^2+T^2}}{\pi d^3}$',
                     r'$\sigma_{eq3}=\dfrac{16\sqrt{F^2+T^2}}{\pi d^3}$',
                     r'$\sigma_{eq3}=\sqrt{\left(\dfrac{4F}{\pi d^2}\right)^2+4\left(\dfrac{16T}{\pi d^3}\right)^2}$',
                     r'$\sigma_{eq3}=\sqrt{\left(\dfrac{4F}{\pi d^2}\right)^2+4\left(\dfrac{32T}{\pi d^3}\right)^2}$']),
    568: dict(stem=(232, 123, 489, 326, 587),
              opts='text', texts=[r'$f_{\mathrm H}>f$', r'$f_{\mathrm H}>nf$',
                                  r'$f_{\mathrm H}<f$', r'$f_{\mathrm H}<nf$']),
    658: dict(stem=(127, 240, 600, 356, 712),
              opts='text', texts=['A', 'B', 'C', 'D']),
    666: dict(stem=(150, 92, 74, 472, 262),
              opts='text', texts=['图（A）', '图（B）', '图（C）', '图（D）']),
    669: dict(stem=(165, 148, 392, 480, 604),
              opts='text', texts=['图（A）', '图（B）', '图（C）', '图（D）']),
    693: dict(stem=(242, 86, 254, 509, 340),
              opts='text', texts=['是图（A）和图（B）', '仅是图（A）', '仅是图（B）', '是图（c）']),
    784: dict(stem=None,
              opts='img', boxes=[(150, 100, 556, 166, 648), (150, 201, 556, 267, 648),
                                 (150, 302, 556, 368, 648), (150, 403, 556, 469, 648)]),
    813: dict(stem=(242, 215, 675, 380, 760),
              opts='img', boxes=[(243, 114, 75, 266, 209), (243, 119, 212, 288, 338),
                                 (243, 114, 340, 267, 474), (243, 114, 479, 280, 601)]),
    904: dict(stem=(151, 145, 585, 455, 655),
              opts='text', texts=['剪力图、弯矩图均不变', '剪力图、弯矩图均改变',
                                  '剪力图不变，弯矩图改变', '剪力图改变，弯矩图不变']),
    908: dict(stem=(163, 236, 112, 344, 232),
              opts='text', texts=['100Mpa', '150MPa', '175Mpa', '25MPa']),
    928: dict(stem=(234, 172, 397, 361, 505),
              opts='text', texts=['信号的谐波结构改变，波形改变', '信号的谐波结构改变，波形不变',
                                  '信号的谐波结构不变，波形不变', '信号的谐波结构不变，波形改变']),
    932: dict(stem=(243, 180, 654, 417, 744),
              opts='text', texts=['OV', '7.07V', '3.18V', '4.5V']),
    1040: dict(stem=(200, 208, 456, 387, 590),
               opts='img', boxes=[(200, 86, 593, 190, 702), (200, 266, 596, 379, 699),
                                  (201, 86, 73, 207, 196), (201, 283, 83, 382, 186)]),
    1050: dict(stem=(224, 86, 676, 289, 745),
               opts='img', boxes=[(225, 114, 76, 318, 114), (225, 114, 122, 318, 162),
                                  (225, 114, 164, 325, 199), (225, 114, 195, 324, 231)]),
    1053: dict(stem=(244, 161, 609, 434, 764),
               opts='text', texts=['图（A）', '图（B）', '图（C）', '图（D）']),
    1262: dict(stem=(130, 176, 179, 420, 243),
               opts='text', texts=['低碳钢扭转破坏', '铸铁扭转破坏', '低碳钢压缩破坏', '铸铁压缩破坏']),
    1292: dict(stem=(245, 168, 557, 427, 641),
               opts='text', texts=['会出现对电源的短路事故', '电路成为半波整流电路',
                                   'D1~D4均无法导通', '输出电压将反相']),
}


def crop(page, x0, y0, x1, y1, name):
    y1 = min(y1, doc[page].rect.height)
    x1 = min(x1, doc[page].rect.width)
    pix = doc[page].get_pixmap(clip=pymupdf.Rect(x0, y0, x1, y1), dpi=DPI)
    fp = os.path.join(OUTDIR, name)
    pix.save(fp)
    return '/images/q23/' + name, pix.width, pix.height


def img_tag(rel):
    return '<img src="%s" style="max-width:100%%;" />' % rel


def strip_imgs(s):
    out, depth = [], 0
    i = 0
    while i < len(s):
        if s.startswith('<img', i):
            j = s.find('>', i)
            i = (j + 1) if j >= 0 else len(s)
            continue
        out.append(s[i]); i += 1
    t = ''.join(out)
    t = t.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
    while '  ' in t:
        t = t.replace('  ', ' ')
    return t.strip()


report = []
for qid, spec in sorted(SPEC.items()):
    q = byid[qid]
    stem_txt = strip_imgs(q.get('question') or '')
    newq = stem_txt
    if spec['stem']:
        rel, w, h = crop(*spec['stem'], 'id%d_stem.png' % qid)
        newq = stem_txt + '<br>' + img_tag(rel)
    q['question'] = newq

    if spec['opts'] == 'text':
        for L, t in zip('ABCD', spec['texts']):
            q[L] = t
        report.append((qid, 'text', spec['texts']))
    else:
        rels = []
        for n, bx in zip('ABCD', spec['boxes']):
            rel, w, h = crop(*bx, 'id%d_opt%s.png' % (qid, n))
            q[n] = img_tag(rel)
            rels.append(rel)
        report.append((qid, 'img', rels))

json.dump(data, open(DB, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
doc.close()

print('\n已修复 %d 题，图片输出到 %s' % (len(report), os.path.relpath(OUTDIR, ROOT)))
for qid, kind, v in report:
    print('  id=%-5s %-4s %s' % (qid, kind, ' | '.join(map(str, v))[:150]))
