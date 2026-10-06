# 用原卷字符级 bbox/字号判定 T2 命中点的数字到底是上标/下标/平排
import json, os, re, sys, unicodedata
import pymupdf

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.abspath(__file__))
SITES = json.load(open(os.path.join(ROOT, '_t2_sites.json'), encoding='utf-8'))
IDX = json.load(open(os.path.join(ROOT, '_t2_srcindex.json'), encoding='utf-8'))

BOOK_OF = {'公共基础': (u'题目和答案pdf/公共基础分类版真题详解（13~24）_题目.pdf',
                        u'题目和答案pdf/公共基础分类版真题详解（13~24）_答案解析.pdf'),
           '专业基础': (u'题目和答案pdf/岩土专业基础分类真题解析（16~24）_题目.pdf',
                        u'题目和答案pdf/岩土专业基础历年真题解析册（2024版）.pdf')}
CJK = re.compile(r'[一-鿿]{4,}')
DIGITS = set('0123456789')
LETTERS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

docs = {}          # path -> fitz doc
charcache = {}     # (path,page) -> char list


def doc_of(path):
    if path not in docs:
        docs[path] = pymupdf.open(os.path.join(ROOT, path))
    return docs[path]


def page_index(path):
    """path -> {page_no: text}"""
    key = ('idx', path)
    if key not in charcache:
        m = {}
        for e in IDX:
            if e['path'] == path:
                m[e['page']] = e['text']
        charcache[key] = m
    return charcache[key]


SUPC = set('¹²³⁰⁴⁵⁷⁸⁹⁻⁼⁽⁾ⁿ')
SUBC = set('₀₁₂₃₄₆₇₈₊₋₌₎')


def chars(path, pno):
    key = (path, pno)
    if key not in charcache:
        pg = doc_of(path)[pno]
        out = []
        for b in pg.get_text('rawdict')['blocks']:
            if b.get('type') != 0:
                continue
            for l in b['lines']:
                for s in l['spans']:
                    for c in s['chars']:
                        nf = unicodedata.normalize('NFKC', c['c'])
                        out.append({'c': c['c'], 'n': nf if len(nf) == 1 else c['c'],
                                    'sup': c['c'] in SUPC, 'sub': c['c'] in SUBC,
                                    'bbox': c['bbox'], 'size': s['size'],
                                    'origin': c['origin'], 'font': s['font']})
        charcache[key] = out
    return charcache[key]


def locate(path, needle):
    """返回按 needle 命中排好序的候选页"""
    m = page_index(path)
    return [p for p, t in sorted(m.items()) if needle in t.replace(' ', '').replace('\n', '')]


DB = json.load(open(os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json'), encoding='utf-8'))
BYID = {q['id']: q for q in DB}


def probes_for(s):
    """该字段全文 -> 题干全文, 依次取中文长串做定位探针"""
    q = BYID.get(s['id'], {})
    texts = [q.get(s['f']) or '', q.get('question') or '', q.get('analysis') or '']
    runs = []
    for t in texts:
        runs.extend(CJK.findall(t or ''))
    runs = [r for r in runs if r.strip()]
    runs.sort(key=len, reverse=True)
    seen, out = set(), []
    for r in runs:
        if r[:8] in seen:
            continue
        seen.add(r[:8])
        out.append(r)
        if len(out) >= 6:
            break
    return out


def nospace(s):
    return re.sub(r'\s+', '', s)


def measure(cs, letter, digits, frag, i, pno=None):
    """在该页字符流里找 (letter, digits...) 相邻对, 量数字相对字母的基线偏移,
       并用题库片段前后文打分, 返回按分数降序的候选"""
    sb = nospace(frag[max(0, i - 10):i])
    sa = nospace(frag[i + 1 + len(digits):i + 1 + len(digits) + 8])
    res = []
    n = len(cs)
    k = 0
    while k < n - 1:
        c = cs[k]['n']
        if c == letter:
            j = k + 1
            gap = 0
            while j < n and cs[j]['n'] in (' ', ' ', ' ', ' ') and gap < 2:
                j += 1
                gap += 1
            ok = True
            for d in digits:
                if j >= n or cs[j]['n'] != d:
                    ok = False
                    break
                j += 1
            if ok:
                after = cs[j]['n'] if j < n else ''
                if after not in DIGITS:
                    bctx = nospace(''.join(x['n'] for x in cs[max(0, k - 12):k]))
                    actx = nospace(''.join(x['n'] for x in cs[j:j + 10]))
                    sc = 0
                    t = 0
                    while t < 6 and t < len(sb) and bctx.endswith(sb[len(sb) - 1 - t]):
                        t += 1
                    sc += 2 * t
                    t = 0
                    while t < 4 and t < len(sa) and actx.startswith(sa[t]):
                        t += 1
                    sc += t
                    d0 = cs[k + 1 + gap]
                    dy = d0['origin'][1] - cs[k]['origin'][1]
                    ratio = d0['size'] / max(cs[k]['size'], 0.1)
                    em = max(cs[k]['size'], 0.1)
                    lig = any(x['sup'] for x in cs[k + 1:j]) or any(x['sub'] for x in cs[k + 1:j])
                    if lig:
                        v = 'SUP' if any(x['sup'] for x in cs[k + 1:j]) else 'SUB'
                    elif dy < -0.18 * em:
                        v = 'SUP'
                    elif dy > 0.18 * em:
                        v = 'SUB'
                    elif ratio < 0.78:
                        v = 'SUP?' if dy < 0 else ('SUB?' if dy > 0 else 'SMALL')
                    else:
                        v = 'INLINE'
                    res.append({'v': v, 'dy': round(dy, 2), 'ratio': round(ratio, 2),
                                'lsize': round(cs[k]['size'], 2), 'dsize': round(d0['size'], 2),
                                'gap': gap, 'lig': lig, 'score': sc, 'page': pno,
                                'bbox': [round(x, 1) for x in d0['bbox']],
                                'lbox': [round(x, 1) for x in cs[k]['bbox']],
                                'before': bctx[-8:], 'after': actx[:8]})
        k += 1
    res.sort(key=lambda x: -x['score'])
    return res


out = []
for s in SITES:
    stem_or_analysis = s['f'] == 'analysis'
    paths = BOOK_OF.get(s['big'])
    if not paths:
        out.append(dict(s, v='NOBOOK'))
        continue
    primary = paths[1] if stem_or_analysis else paths[0]
    secondary = paths[0] if stem_or_analysis else paths[1]
    probes = probes_for(s)

    def scan(path, probes=probes, s=s):
        pages = []
        for pr in probes:
            for ln in (12, 10, 8, 6, 4):
                if len(pr) < ln:
                    continue
                for p in locate(path, pr[:ln]):
                    if p not in pages:
                        pages.append(p)
                if len(pages) >= 6:
                    break
            if len(pages) >= 6:
                break
        found = []
        for pno in pages[:6]:
            found.extend(measure(chars(path, pno), s['letter'], s['digits'], s['frag'], s['i'], pno))
        found.sort(key=lambda x: -x['score'])
        return pages, found

    pages, found = scan(primary)
    path = primary
    if not found:
        pages2, found2 = scan(secondary)
        if found2:
            pages, found, path = pages2, found2, secondary
    if not found:
        out.append(dict(s, v='NOTLOCATED' if not pages else 'NOMATCH',
                        path=os.path.basename(path), pages=pages[:6],
                        probe=probes[0][:10] if probes else None))
        continue
    top = found[0]['score']
    grp = [f for f in found if f['score'] == top] if top > 0 else found
    vs = [f['v'] for f in grp]
    if top == 0:
        v = 'WEAK'
    elif len(set(vs)) == 1:
        v = vs[0]
    else:
        v = 'AMBIG'
    out.append(dict(s, v=v, score=top, all=vs, path=os.path.basename(path), pages=pages[:6],
                    probe=probes[0][:10] if probes else None, sample=found[:3]))

json.dump(out, open(os.path.join(ROOT, '_t2_verdicts.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

tally = {}
for o in out:
    tally[o['v']] = tally.get(o['v'], 0) + 1
qs = {}
for o in out:
    qs.setdefault(o['v'], set()).add(o['id'])
L = ['量测结果 站点=%d' % len(out)]
for k in sorted(tally, key=lambda x: -tally[x]):
    L.append('  %-12s 站点=%3d 题数=%3d' % (k, tally[k], len(qs[k])))
open(os.path.join(ROOT, '_t2_measure.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('done')
