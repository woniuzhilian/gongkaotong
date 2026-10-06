# 诊断 NOMATCH: 打印指定页里目标字母出现处的归一字符流
import json, os, sys, unicodedata
import pymupdf

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(ROOT, '_t2_verdicts.json'), encoding='utf-8'))
TARGETS = [(x['id'], x['letter'], x['digits'], x['path'], x['pages'][0]) for x in V if x['v'] == 'NOMATCH'][:6]
BOOK = {
    u'公共基础分类版真题详解（13~24）_题目.pdf': u'题目和答案pdf/公共基础分类版真题详解（13~24）_题目.pdf',
    u'公共基础分类版真题详解（13~24）_答案解析.pdf': u'题目和答案pdf/公共基础分类版真题详解（13~24）_答案解析.pdf',
}
L = []
for qid, letter, digits, pname, pno in TARGETS:
    path = BOOK.get(pname)
    if not path:
        L.append('skip %s' % pname); continue
    d = pymupdf.open(os.path.join(ROOT, path))
    pg = d[pno]
    cs = []
    for b in pg.get_text('rawdict')['blocks']:
        if b.get('type') != 0:
            continue
        for l in b['lines']:
            for s in l['spans']:
                for c in s['chars']:
                    nf = unicodedata.normalize('NFKC', c['c'])
                    cs.append((nf if len(nf) == 1 else c['c'], c['c'], round(s['size'], 2),
                               round(c['origin'][1], 1)))
    stream = ''.join(x[0] for x in cs)
    L.append('=== id=%s letter=%s digits=%s page=%s streamlen=%d' % (qid, letter, digits, pno, len(cs)))
    idxs = [k for k, x in enumerate(cs) if x[0] == letter]
    L.append('  出现 %d 次; 样例(归一/原始/字号/基线):' % len(idxs))
    for k in idxs[:14]:
        w = cs[k:k + 4]
        L.append('    @%-5d %s' % (k, ' | '.join('%r/%r/%s/%s' % (a, b, c, e) for a, b, c, e in w)))
open(os.path.join(ROOT, '_t2_diag.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')
