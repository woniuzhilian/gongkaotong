# -*- coding: utf-8 -*-
"""T2：从原书 span 几何提取 (基字符, 上下标内容, 上/下) 事实表，回填到题库现值的塌陷处。
   只产出提案，不写库。"""
import os, re, io, json, collections, unicodedata
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
P = os.path.join(ROOT, '题目和答案pdf')
BK = os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf')
BKQ = os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf')
OUT = io.open(os.path.join(ROOT, '_t2_prop.txt'), 'w', encoding='utf-8')
data = json.load(open(DB, encoding='utf-8'))
byid = {q['id']: q for q in data}
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']
CJK = re.compile(r'[一-鿿]{4,}')
HDR = re.compile(r'【\s*(\d{4})\s*[-—]\s*(\d{1,3})\s*】')
B = chr(92)

doc = pymupdf.open(BK)
docq = pymupdf.open(BKQ)

GK = {'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta', 'ε': 'varepsilon', 'ζ': 'zeta',
      'η': 'eta', 'θ': 'theta', 'ι': 'iota', 'κ': 'kappa', 'λ': 'lambda', 'μ': 'mu',
      'ν': 'nu', 'ξ': 'xi', 'ρ': 'rho', 'σ': 'sigma', 'ς': 'sigma', 'τ': 'tau',
      'υ': 'upsilon', 'φ': 'phi', 'χ': 'chi', 'ψ': 'psi', 'ω': 'omega', 'π': 'pi',
      'Γ': 'Gamma', 'Δ': 'Delta', 'Θ': 'Theta', 'Λ': 'Lambda', 'Ξ': 'Xi', 'Π': 'Pi',
      'Σ': 'Sigma', 'Φ': 'Phi', 'Ψ': 'Psi', 'Ω': 'Omega', '∞': 'infty'}


def norm(ch):
    """字符 -> 题库里的书写形式（ASCII 字母 或 \\命令）"""
    n = unicodedata.normalize('NFKC', ch)
    if len(n) != 1:
        return None
    if n in GK:
        return B + GK[n]
    if n.isascii() and (n.isalpha() or n.isdigit()):
        return n
    return None


def flat(s):
    return re.sub(r'\s+', '', s)


PAGEC = {}
BLOCKC = {}


def page_text(d, tag, pno):
    k = (tag, pno)
    if k not in PAGEC:
        PAGEC[k] = flat(d[pno].get_text())
    return PAGEC[k]


def page_blocks(d, tag, pno):
    k = (tag, pno)
    if k not in BLOCKC:
        BLOCKC[k] = sorted([b for b in d[pno].get_text('blocks') if b[4].strip()], key=lambda b: b[1])
    return BLOCKC[k]


def entry_blocks(d, text, tag):
    """按探针定位题目所属册子条目，返回该条目覆盖的块列表"""
    probes = sorted(CJK.findall(re.sub(r'\$[^$]*\$', ' ', text)), key=len, reverse=True)[:3]
    if not probes:
        return None
    for pno in range(d.page_count):
        if probes[0] in page_text(d, tag, pno):
            pg = d[pno]
            bs = page_blocks(d, tag, pno)
            for i, b in enumerate(bs):
                if probes[0] in flat(b[4]):
                    lo = i
                    while lo > 0 and not HDR.search(bs[lo][4]) and '【考点分析】' not in bs[lo][4] and '【解析】' not in bs[lo][4]:
                        lo -= 1
                    hi = i
                    while hi + 1 < len(bs) and not HDR.search(bs[hi + 1][4]):
                        hi += 1
                    return pg, bs[lo:hi + 1]
    return None


def scripts_from_blocks(pg, blocks):
    """扫描条目内每个块，返回 {(基字符, 下标内容): '^' or '_'} 与歧义集合"""
    pairs = {}
    ambig = set()
    ev = collections.defaultdict(list)
    for b in blocks:
        raw = pg.get_text('rawdict', clip=pymupdf.Rect(b[:4]))
        for blk in raw['blocks']:
            for ln in blk.get('lines', []):
                sp = []
                for s in ln.get('spans', []):
                    txt = ''.join(c['c'] for c in s.get('chars', []))
                    if txt:
                        sp.append({'t': txt, 'sz': s['size'], 'y': s['origin'][1], 'x': s['origin'][0]})
                if not sp:
                    continue
                szc = collections.Counter(round(x['sz'], 1) for x in sp)
                base_sz = szc.most_common(1)[0][0]
                same = [x for x in sp if abs(x['sz'] - base_sz) <= 0.6]
                if not same:
                    continue
                base_y = collections.Counter(round(x['y'], 1) for x in same).most_common(1)[0][0]
                sp = sorted(sp, key=lambda x: x['x'])
                for j, x in enumerate(sp):
                    if j == 0:
                        continue
                    prev = sp[j - 1]
                    if abs(x['sz'] - base_sz) > 0.6:
                        # 与前一 span 的基线比较：积分限整体下沉时行众数基线会误判
                        tag = '^' if x['y'] < prev['y'] - 0.8 else '_'
                        if abs(x['y'] - prev['y']) <= 0.8:
                            tag = '^' if x['y'] < base_y - 0.8 else '_'
                        if len(prev['t']) and len(x['t']) <= 3:
                            bk = norm(prev['t'][-1])
                            ck = ''.join([norm(c) or '' for c in x['t']])
                            if bk and ck and re.fullmatch(r'(\\?[A-Za-z0-9]+)', ck):
                                key = (bk, ck)
                                if key in pairs and pairs[key] != tag:
                                    ambig.add(key)
                                pairs[key] = tag
                                ev[key].append(prev['t'][-6:] + ('^' if tag == '^' else '_') + x['t'])
    return pairs, ambig, ev


stats = collections.Counter()
EDITS = {}
for q in data:
    tid = q['id']
    allt = ' '.join(str(q.get(f) or '') for f in FIELDS)
    if '$' not in allt:
        continue
    ent = entry_blocks(doc, str(q.get('analysis') or '') + ' ' + str(q.get('question') or ''), 'A')
    entq = entry_blocks(docq, str(q.get('question') or ''), 'Q')
    pairs, ambig, ev = {}, {}, {}
    pa, aa, ea = ({}, set(), {})
    if ent:
        pa, aa, ea = scripts_from_blocks(ent[0], ent[1])
        pairs.update(pa); ev.update(ea)
    if entq:
        pb, ab, eb = scripts_from_blocks(entq[0], entq[1])
        aa = aa | ab
        for k, v in pb.items():
            if k in pairs and pairs[k] != v:
                aa = aa | {k}
            pairs[k] = v
            ev.setdefault(k, []).extend(eb.get(k, []))
    ambig = set(ambig) | aa
    stats['题:定位到条目' if (ent or entq) else '题:未定位'] += 1
    for f in FIELDS:
        t = str(q.get(f) or '')
        if not t:
            continue
        for m in re.finditer(r'\$([^$]+)\$', t):
            inner = m.group(1)
            for mm in re.finditer('((?:' + B + B + '[A-Za-z]+)|[A-Za-z])([0-9]{1,3})(?![0-9A-Za-z.])', inner):
                base, dig = mm.group(1), mm.group(2)
                stats['候选点'] += 1
                key = (base, dig)
                if key in ambig:
                    stats['歧义跳过'] += 1
                    continue
                if key not in pairs:
                    stats['原书无此配对'] += 1
                    continue
                stats['可提案'] += 1
                EDITS.setdefault(str(tid), {}).setdefault(f, {})[base + '|' + dig] = pairs[key]
                OUT.write('id=%d %s  %s%s -> %s%s{%s}   证据=%s\n' % (
                    tid, f, base, dig, base, pairs[key], dig, ' | '.join(ev[key][:2])))
json.dump(EDITS, open(os.path.join(ROOT, '_t2_edits.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
OUT.write('\n' + '=' * 40 + '\n')
for k in sorted(stats):
    OUT.write('%s: %d\n' % (k, stats[k]))
OUT.close()
print(' | '.join('%s=%d' % (k, stats[k]) for k in sorted(stats)))
