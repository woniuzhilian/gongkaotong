# -*- coding: utf-8 -*-
"""#5：从原书 Cambria Math span 判定 : ; 的真实身份（+/-），按局部字符键回填题库。
   只产出提案，不写库。依据：原书里真冒号后必跟空格/跨 span，错位的 +/− 与操作数粘连。"""
import os, re, io, json, sys, collections, unicodedata
import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
ARG = sys.argv[1:]
ALL = bool(ARG) and ARG[0] == '--all'
DBG = set(int(x) for x in (ARG[1:] if ALL else ARG) if x.lstrip('-').isdigit())
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
P = os.path.join(ROOT, '题目和答案pdf')
BK = os.path.join(P, '公共基础分类版真题详解（13~24）_答案解析.pdf')
BKQ = os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf')
OUT = io.open(os.path.join(ROOT, '_t5_prop.txt'), 'w', encoding='utf-8')
data = json.load(io.open(DB, encoding='utf-8'))
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']
CJK = re.compile(r'[一-鿿]{4,}')
HAN = re.compile(r'[一-鿿]')
HDR = re.compile(r'【\s*(\d{4})\s*[-—]\s*(\d{1,3})\s*】')
B = chr(92)
CMDRE = re.compile(B + B + '[A-Za-z]+')
SP = set(' ' + chr(10) + chr(9) + chr(160) + chr(8195) + chr(8194) + chr(8201)
         + chr(8202) + chr(8239) + chr(8287) + chr(8203) + chr(12288))
INVIS = set(chr(0x2061) + chr(0x2062) + chr(0x2063) + chr(0x2064))
N = 3
MINCTX = int(os.environ.get('MINCTX', '2'))
NEW = {':': '+', ';': '-'}


def norm(ch):
    """字符 -> 键原语；希腊字母/偏导等一律丢弃，避免两侧书写差异造成键不匹配"""
    n = unicodedata.normalize('NFKC', ch)
    if len(n) != 1:
        return None
    if n.isascii() and (n.isalpha() or n.isdigit()):
        return n
    return None


def flat(s):
    return re.sub(r'\s+', '', s)


PAGEC = {}
BLOCKC = {}
RAWC = {}


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


def page_raw(d, tag, pno):
    k = (tag, pno)
    if k not in RAWC:
        RAWC[k] = d[pno].get_text('rawdict')
    return RAWC[k]


def probes_of(t):
    return sorted(set(CJK.findall(re.sub(r'\$[^$]*\$', ' ', t))), key=len, reverse=True)[:6]


def entry_rect(d, tag, text, probes=None):
    """定位条目，返回 (页号, 条目矩形, 命中探针数)；命中探针 >=2 才接受，避免考点分析套话串题"""
    ps = probes if probes is not None else probes_of(text)
    ps = [p for p in ps if len(p) >= 4]
    if len(ps) < 2:
        return None
    best = None
    for pno in range(d.page_count):
        pt = page_text(d, tag, pno)
        if not any(p in pt for p in ps):
            continue
        bs = page_blocks(d, tag, pno)
        for i, b in enumerate(bs):
            bt = flat(b[4])
            if not any(p in bt for p in ps):
                continue
            lo = i
            while lo > 0:
                pv = bs[lo - 1][4]
                if HDR.search(pv) or '【考点分析】' in pv or '【解析】' in pv:
                    break
                lo -= 1
            hi = i
            while hi + 1 < len(bs) and not HDR.search(bs[hi + 1][4]):
                hi += 1
            seg = flat(''.join(bs[j][4] for j in range(lo, hi + 1)))
            hit = sum(1 for p in ps if p in seg)
            if best is None or hit > best[2]:
                r = pymupdf.Rect(bs[lo][:4])
                for j in range(lo + 1, hi + 1):
                    r |= pymupdf.Rect(bs[j][:4])
                best = (pno, r, hit)
    return best if best and best[2] >= 2 else None


def entry_lines(d, tag, pno, rect):
    """整页 span 过滤到条目矩形内，按行返回；每行是 span 列表"""
    out = []
    rd = page_raw(d, tag, pno)
    for blk in rd['blocks']:
        for ln in blk.get('lines', []):
            sp = []
            y0 = ln['bbox'][1]
            for s in ln.get('spans', []):
                txt = ''.join(c['c'] for c in s.get('chars', []))
                if not txt:
                    continue
                x0, sy = s['bbox'][0], s['bbox'][1]
                if not (rect.x0 - 2 <= x0 <= rect.x1 + 2 and rect.y0 - 2 <= sy <= rect.y1 + 2):
                    continue
                sp.append({'t': txt, 'sz': s['size'], 'x': x0, 'f': s['font']})
            if sp:
                out.append((round(y0, 1), min(z['x'] for z in sp), sp))
    out.sort(key=lambda z: (z[0], z[1]))
    return [z[2] for z in out]


WORDS = ['arctan', 'arcsin', 'arccos', 'log', 'lim', 'ln', 'lg', 'exp', 'sin', 'cos',
         'tan', 'cot', 'sec', 'csc', 'max', 'min', 'sgn', 'arccot', 'arcsec']


def mk_atoms(chars):
    a, p = [], []
    for i, c in enumerate(chars):
        k = norm(c)
        if k:
            a.append(k)
            p.append(i)
    txt = ''.join(a)
    kill = [False] * len(a)
    for w in WORDS:
        st = 0
        while True:
            j = txt.find(w, st)
            if j < 0:
                break
            for k in range(j, j + len(w)):
                kill[k] = True
            st = j + len(w)
    return [x for x, d in zip(a, kill) if not d], [y for y, d in zip(p, kill) if not d]


def key_of(atoms, pos, i, n=N):
    j = 0
    while j < len(pos) and pos[j] < i:
        j += 1
    a = atoms[max(0, j - n):j]
    c = atoms[j:j + n]
    return ''.join(a) + '|' + ''.join(c), len(a), len(c)


def book_sites(lines):
    res = []
    for sp in lines:
        sp = sorted(sp, key=lambda x: x['x'])
        mathsp = [x for x in sp if 'Math' in x['f'] or 'Cambria' in x['f']]
        pool = mathsp or sp
        cnt = collections.Counter(round(x['sz'], 1) for x in pool)
        base_sz = cnt.most_common(1)[0][0]
        stream, meta = [], []
        for x in sp:
            for ch in x['t']:
                if ch in INVIS:
                    continue
                stream.append(ch)
                meta.append((x['sz'], x['f']))
        atoms, pos = mk_atoms(stream)
        for idx, ch in enumerate(stream):
            if ch != ':' and ch != ';':
                continue
            sz, fnt = meta[idx]
            if 'Math' not in fnt and 'Cambria' not in fnt:
                continue
            nxt = stream[idx + 1] if idx + 1 < len(stream) else ''
            prv = stream[idx - 1] if idx > 0 else ''
            if nxt == '' or nxt in SP or prv == '' or prv in SP:
                continue
            if not (norm(nxt) or nxt in '(['):
                continue
            if not (norm(prv) or prv in ')]'):
                continue
            k, nb, na = key_of(atoms, pos, idx)
            res.append({'key': k, 'ch': ch, 'new': NEW[ch], 'nb': nb, 'na': na,
                        'script': sz < base_sz - 0.6,
                        'raw': ''.join(stream[max(0, idx - 12):idx + 13])})
    return res


def math_spans(t):
    """按 KaTeX 的配对规则切出 $...$ 区间"""
    r, s = [], -1
    for i, c in enumerate(t):
        if c != '$':
            continue
        if s < 0:
            s = i
        else:
            r.append((s, i))
            s = -1
    return r


def inspan(spans, i):
    return any(a < i < b for a, b in spans)


def db_stream(t):
    keep = []
    i = 0
    n = len(t)
    while i < n:
        if t[i] == B:
            m = CMDRE.match(t, i)
            i = m.end() if m else i + 1
            keep.append(' ')
            continue
        keep.append(t[i])
        i += 1
    return mk_atoms(keep)


def in_script_group(t, i):
    stack = []
    for j in range(i):
        c = t[j]
        if c == '{':
            stack.append(j > 0 and t[j - 1] in '^_')
        elif c == '}' and stack:
            stack.pop()
    return any(stack)


doc = pymupdf.open(BK)
docq = pymupdf.open(BKQ)
stats = collections.Counter()
EDITS = {}
SITES = []
CAND = []
for q in data:
    tid = q['id']
    if DBG and tid not in DBG:
        continue
    CONFPOS = set(e[0:2] for v in EDITS.get(str(tid), {}).values() for e in v)
    allt = ' '.join(str(q.get(f) or '') for f in FIELDS)
    if ':' not in allt and ';' not in allt:
        continue
    qpr = probes_of(str(q.get('question') or ''))
    apr = probes_of(str(q.get('analysis') or ''))
    cpr = sorted(set(qpr) | set(apr), key=len, reverse=True)[:6]
    ea = (entry_rect(doc, 'A', '', cpr) or entry_rect(doc, 'A', '', apr)
          or entry_rect(doc, 'A', '', qpr))
    eq = (entry_rect(docq, 'Q', '', cpr) or entry_rect(docq, 'Q', '', qpr))
    if not ea and not eq:
        stats['题:两书未定位'] += 1
        continue
    stats['题:定位到条目'] += 1
    NS = 0
    bs = []
    for d, tag, e in ((doc, 'A', ea), (docq, 'Q', eq)):
        if not e:
            continue
        bs += book_sites(entry_lines(d, tag, e[0], e[1]))
    bykey = collections.defaultdict(list)
    scrk = set()
    for s in bs:
        if s['script']:
            scrk.add(s['key'])
        if s['script']:
            stats['书证:上下标位（需补花括号，本轮不动）'] += 1
            continue
        if s['nb'] < MINCTX or s['na'] < MINCTX:
            stats['书证:上下文太短跳过'] += 1
            continue
        bykey[s['key']].append(s)
    conf = set()
    for k, v in bykey.items():
        if len(set((x['new'], x['ch']) for x in v)) > 1:
            conf.add(k)
            stats['书证:键内冲突'] += 1
    DET = []
    if DBG or ALL:
        DET.append('\n##### id=%d 书证点=%d 可用键=%d' % (tid, len(bs), len(bykey)))
        for s in bs:
            DET.append('  BOOK k=%-20s %s->%s scr=%d nb=%d na=%d  …%s…' % (
                s['key'], s['ch'], s['new'], s['script'], s['nb'], s['na'], s['raw']))
        DET.append('  KEYS ' + ' '.join(sorted(bykey)))
    for f in FIELDS:
        t = str(q.get(f) or '')
        if not t or (':' not in t and ';' not in t):
            continue
        atoms, pos = db_stream(t)
        spans = math_spans(t)
        frag = {}
        for a, b in spans:
            for j in range(a + 1, b):
                frag[j] = (a, b)
        cand = collections.defaultdict(list)
        for i, c in enumerate(t):
            if c != ':' and c != ';':
                continue
            if i not in frag:
                stats['题内:片段外跳过'] += 1
                continue
            a, b = frag[i]
            if HAN.search(t[a + 1:b]):
                stats['题内:片段含中文($定界错)'] += 1
                continue
            if re.match(r'^\s*[A-Za-z]{1,3}\s*[:;]', t[a + 1:i + 1]):
                stats['题内:标签冒号跳过'] += 1
                continue
            nx = t[i + 1] if i + 1 < b else ''
            if t[i - 1] in 'eE' and (norm(nx) or nx in '(['):
                stats['题内:e后疑似丢负指数'] += 1
                continue
            k, nb, na = key_of(atoms, pos, i)
            NS += 1
            CAND.append('%-5d %-8s %4d %s %-11s …%s…' % (
                tid, f, i, c, '★' if (str(tid), f, i) in CONFPOS else (
                    '书' + '/'.join(sorted(set(x['ch'] + x['new'] for x in bykey[k]))))
                if k in bykey else '', t[max(0, i - 34):i] + '«' + c + '»' + t[i + 1:i + 35]))
            cand[k].append((i, c, nb, na))
        if DBG or ALL:
            DET.append('  ---- DB %s: %s' % (f, t))
            for k, lst in cand.items():
                for (i, c, nb, na) in lst:
                    DET.append('     DB @%d %s k=%-20s nb=%d na=%d inbook=%d  …%s…' % (
                        i, c, k, nb, na, k in bykey, t[max(0, i - 12):i + 13]))
        for k, lst in cand.items():
            if k in conf:
                continue
            if k not in bykey:
                stats['原书无此符号点'] += 1
                if k in scrk:
                    stats['其中:原书该点被判为上下标'] += 1
                continue
            if len(set(x[1] for x in lst)) != 1:
                stats['题内同键字符不一致'] += 1
                continue
            s = bykey[k][0]
            for (i, c, nb, na) in lst:
                if nb < MINCTX or na < MINCTX:
                    stats['题内上下文太短'] += 1
                    continue
                if in_script_group(t, i):
                    stats['题内已在花括号内'] += 1
                    continue
                if s['ch'] != c:
                    stats['字符不一致跳过'] += 1
                    continue
                stats['可提案'] += 1
                EDITS.setdefault(str(tid), {}).setdefault(f, []).append([i, c, s['new'], k])
                SITES.append('id=%d %s @%d  %s -> %s  键=%-20s 书证=…%s…' % (
                    tid, f, i, c, s['new'], k, s['raw']))
    if NS:
        stats['题:含数学符号点'] += 1
        stats['数学符号点'] += NS
        if DBG or ALL:
            OUT.write('\n'.join(DET) + '\n')
doc.close()
docq.close()
for line in SITES:
    OUT.write(line + '\n')
OUT.write('\n' + '=' * 40 + '\n')
for k in sorted(stats):
    OUT.write('%s: %d\n' % (k, stats[k]))
for line in CAND:
    OUT.write(line + chr(10))
OUT.close()
json.dump(EDITS, io.open(os.path.join(ROOT, '_t5_edits.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('q=%d f=%d sites=%d | ' % (len(EDITS), sum(len(v) for v in EDITS.values()),
                                 sum(len(x) for v in EDITS.values() for x in v.values()))
      + ' | '.join('%s=%d' % (k, stats[k]) for k in sorted(stats)).encode('unicode_escape').decode())
