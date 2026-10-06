# 原卷定位索引: 按 【YYYY-NN】 切段, 再用题干散文探针把题库题目映射到 (书, 页, 段)
import json, os, re, sys
import pymupdf

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.abspath(__file__))
BOOKS = [
    ('公共基础', u'题目和答案pdf/公共基础分类版真题详解（13~24）_题目.pdf'),
    ('公共基础', u'题目和答案pdf/公共基础分类版真题详解（13~24）_答案解析.pdf'),
    ('专业基础', u'题目和答案pdf/岩土专业基础历年真题解析册（2024版）.pdf'),
]
MARK = re.compile(r'【\s*(\d{4})\s*[-–—]\s*(\d{1,3})\s*】')
HAN = u'一-鿿'
PROBE = re.compile(u'[' + HAN + u']{2,}')


def norm(s):
    return re.sub(u'[^' + HAN + u'0-9A-Za-z]', u'', s)


def segments(pgtext):
    """把一页文本按标记切段 -> [(year,num,text)]"""
    hits = list(MARK.finditer(pgtext))
    out = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(pgtext)
        out.append((m.group(1), m.group(2), pgtext[m.end():end]))
    return out, hits


idx = []
for tag, path in BOOKS:
    full = os.path.join(ROOT, path)
    d = pymupdf.open(full)
    for pno in range(d.page_count):
        pg = d[pno]
        txt = pg.get_text()
        segs, hits = segments(txt)
        if not hits:
            continue
        idx.append({'book': tag, 'path': path, 'page': pno,
                    'segs': [{'y': a, 'n': b, 'probe': [p[:8] for p in PROBE.findall(c)][:6],
                              'norm': norm(c)[:400]} for a, b, c in segs],
                    'text': txt})
    print(tag, os.path.basename(path), 'pages-with-markers', len({e['page'] for e in idx if e['path'] == path}))

json.dump(idx, open(os.path.join(ROOT, '_t2_srcindex.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('index entries', len(idx))
