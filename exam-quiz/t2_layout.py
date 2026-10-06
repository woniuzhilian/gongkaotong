# -*- coding: utf-8 -*-
"""T2 原型：用 PDF span 的字号+基线判定上下标，重建公式并与题库现值对照"""
import os, re, io, json, collections
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
P = os.path.join(ROOT, '题目和答案pdf')
BK = os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf')
BKQ = os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf')
OUT = io.open(os.path.join(ROOT, '_t2_layout.txt'), 'w', encoding='utf-8')
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
CJK = re.compile(r'[一-鿿]{4,}')
doc = pymupdf.open(BK)
docq = pymupdf.open(BKQ)


def flat(s):
    return re.sub(r'\s+', '', s)


def find_block(d, text, want='【解析】'):
    probes = sorted(CJK.findall(re.sub(r'\$[^$]*\$', ' ', text)), key=len, reverse=True)[:3]
    if not probes:
        return None, None, None
    for pno in range(d.page_count):
        if probes[0] in flat(d[pno].get_text()):
            pg = d[pno]
            bs = sorted([b for b in pg.get_text('blocks') if b[4].strip()], key=lambda b: b[1])
            for i, b in enumerate(bs):
                if probes[0] in flat(b[4]):
                    return pg, bs, i
    return None, None, None


def reconstruct(pg, b):
    """返回 (重建串, 诊断行列表)。b 是 block 元组"""
    raw = pg.get_text('rawdict', clip=pymupdf.Rect(b[:4]))
    lines = []
    for blk in raw['blocks']:
        for ln in blk.get('lines', []):
            spans = []
            for sp in ln.get('spans', []):
                txt = ''.join(ch['c'] for ch in sp.get('chars', []))
                if not txt:
                    continue
                spans.append({'t': txt, 'sz': sp['size'], 'y': sp['origin'][1],
                              'x': sp['origin'][0]})
            if spans:
                lines.append(spans)
    diag = []
    out = []
    for spans in lines:
        sizes = collections.Counter(round(s['sz'], 1) for s in spans)
        base = sizes.most_common(1)[0][0]
        ys = collections.Counter(round(s['y'], 1) for s in spans)
        basey = ys.most_common(1)[0][0]
        spans = sorted(spans, key=lambda s: s['x'])
        for s in spans:
            tag = ''
            if abs(s['sz'] - base) > 0.6:
                tag = '^' if s['y'] < basey - 0.8 else '_'
            diag.append('   sz=%.1f y=%.1f base=%.1f/%.1f tag=%r %r' % (
                s['sz'], s['y'], base, basey, tag, s['t'][:40]))
            if tag:
                out.append(tag + '{' + s['t'] + '}')
            else:
                out.append(s['t'])
        out.append('\n')
    return ''.join(out), diag


JOBS = [(24, 'question'), (24, 'analysis'), (121, 'question'), (5, 'analysis')]
for tid, f in JOBS:
    q = byid[tid]
    t = str(q.get(f) or '')
    d = docq if f == 'question' else doc
    pg, bs, i = find_block(d, t)
    OUT.write('=' * 78 + '\n')
    OUT.write('id=%d %s  现值: %s\n' % (tid, f, t))
    if pg is None:
        OUT.write('  !! 未定位\n')
        continue
    OUT.write('  块原文: %s\n' % bs[i][4].replace('\n', ' ')[:200])
    rec, diag = reconstruct(pg, bs[i])
    OUT.write('  --- 重建(带上下标标记) ---\n%s\n' % rec)
    OUT.write('  --- span 诊断 ---\n%s\n' % '\n'.join(diag[:60]))
OUT.close()
print('ok')
