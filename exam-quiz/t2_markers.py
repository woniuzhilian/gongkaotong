# 建立原卷标记索引: 扫描分类版 PDF 的 【YYYY-NN】 标记 -> (页, y, 该题文字块)
import json, os, re, sys
import pymupdf

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.abspath(__file__))
BOOKS = {
    'gongong': [u'题目和答案pdf/公共基础分类版真题详解（13~24）_题目.pdf',
                u'题目和答案pdf/公共基础分类版真题详解（13~24）_答案解析.pdf'],
    'zhuanye': [u'题目和答案pdf/岩土专业基础历年真题解析册（2024版）.pdf',
                u'题目和答案pdf/岩土专业基础分类真题解析（16~24）_题目.pdf'],
}
MARK = re.compile(r'【\s*(\d{4})\s*[-–—]\s*(\d{1,3})\s*】')

def page_spans(pg):
    out = []
    for b in pg.get_text('dict')['blocks']:
        if b.get('type') != 0:
            continue
        for l in b['lines']:
            for s in l['spans']:
                out.append({'text': s['text'], 'size': round(s['size'], 2),
                            'bbox': [round(v, 1) for v in s['bbox']], 'font': s['font']})
    return out

idx = {}
for tag, paths in BOOKS.items():
    for pi, path in enumerate(paths):
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            print('MISSING', path); continue
        d = pymupdf.open(full)
        n = 0
        for pno in range(d.page_count):
            for sp in page_spans(d[pno]):
                m = MARK.search(sp['text'])
                if m:
                    key = (tag, pi, pno, m.group(1), m.group(2))
                    idx[str(key)] = {'book': path, 'page': pno, 'marker': sp['text'][:24],
                                     'bbox': sp['bbox'], 'size': sp['size']}
                    n += 1
        print('%s part%d %s -> markers=%d pages=%d' % (tag, pi, os.path.basename(path), n, d.page_count))
json.dump(idx, open(os.path.join(ROOT, '_t2_markers.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('total markers', len(idx))
