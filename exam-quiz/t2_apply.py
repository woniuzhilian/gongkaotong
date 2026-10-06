# -*- coding: utf-8 -*-
"""T2 上下标塌陷修复：按 _t2_edits.json（原书版式几何证据推导）回填 base^{}{}/base_{}{}。
用法: py t2_apply.py --dry | py t2_apply.py"""
import os, re, sys, json, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
BAK = os.path.join(ROOT, '_fix_backup', 'questions_BEFORE_T2.json')
ED = os.path.join(ROOT, '_t2_edits.json')
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']
B = chr(92)

# 651/965 的题干解析整体错位（`x2^{2}x^{2}` 这类残留），机械回填会叠出 x^{2}^{2}，留给整段重录
SKIP = {651, 965}

# 与 t2_prop.py 的候选点正则保持一致，否则回填位置与提案对不上
PAT = re.compile('((?:' + B + B + '[A-Za-z]+)|[A-Za-z])([0-9]{1,3})(?![0-9A-Za-z.])')


def fix_field(txt, emap, used):
    """只在 $...$ 片段内替换，命中 emap 的 (base,dig) 才改"""
    hits = 0

    def one(m):
        nonlocal hits
        base, dig = m.group(1), m.group(2)
        key = base + '|' + dig
        tag = emap.get(key)
        if tag is None:
            return m.group(0)
        used[key] = used.get(key, 0) + 1
        hits += 1
        return base + tag + '{' + dig + '}'

    out, pos = [], 0
    for m in re.finditer(r'\$([^$]+)\$', txt):
        out.append(txt[pos:m.start()])
        out.append('$' + PAT.sub(one, m.group(1)) + '$')
        pos = m.end()
    out.append(txt[pos:])
    return ''.join(out), hits


def check(tid, fld, old, new):
    bad = []
    if new.count('$') % 2:
        bad.append('odd-$')
    if '$$' in new:
        bad.append('adj-$$')
    if new.endswith(B) and not old.endswith(B):
        bad.append('trailing-backslash')
    # 叠挂：原本已有上下标的地方又被塞进一层
    if re.search(r'[_^]\{[^{}]*\}\s*[_^]\{', new) and not re.search(r'[_^]\{[^{}]*\}\s*[_^]\{', old):
        bad.append('double-script')
    if re.search(r'\{\}[_^]', new) or re.search(r'[_^]\{\}', new):
        bad.append('empty-outer')
    return ['%s/%s: %s' % (tid, fld, x) for x in bad]


def main():
    edits = json.load(open(ED, encoding='utf-8'))
    data = json.load(open(DB, encoding='utf-8'))
    byid = {q['id']: q for q in data}
    problems, changed, used, nhit = [], {}, {}, 0
    eids = {int(k) for k in edits}
    skipped = sorted(eids & SKIP)

    for q in data:
        tid = q['id']
        if tid not in eids or tid in SKIP:
            continue
        for f in FIELDS:
            v = q.get(f)
            if not isinstance(v, str) or not v:
                continue
            emap = edits[str(tid)].get(f)
            if not emap:
                continue
            nv, h = fix_field(v, emap, used.setdefault((tid, f), {}))
            if h:
                nhit += h
                problems += check(tid, f, v, nv)
                changed.setdefault(tid, {})[f] = (v, nv)
            for k in emap:
                if not used.get((tid, f), {}).get(k):
                    problems.append('NO-HIT %s/%s: %s' % (tid, f, k))

    rep = []
    rep.append('提案: 题=%d 字段=%d 配对=%d' % (
        len(edits), sum(len(v) for v in edits.values()),
        sum(len(g) for v in edits.values() for g in v.values())))
    rep.append('实改: 题=%d 字段=%d 处=%d' % (len(changed), sum(len(v) for v in changed.values()), nhit))
    rep.append('跳过(留给整段重录): 题=%d %s' % (len(skipped), skipped))
    rep.append('校验问题数=%d' % len(problems))
    for p in problems:
        rep.append('  !! ' + p)
    for tid in sorted(changed):
        rep.append('---- id=%d' % tid)
        for f, (a, b) in changed[tid].items():
            rep.append('  [%s] - %s' % (f, a))
            rep.append('  [%s] + %s' % (f, b))
    with open(os.path.join(ROOT, '_t2_apply.txt'), 'w', encoding='utf-8', newline='\r\n') as fh:
        fh.write('\n'.join(rep))
    json.dump({str(k): {f: v[1] for f, v in d.items()} for k, d in changed.items()},
              open(os.path.join(ROOT, '_t2_new.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('changed_q=%d changed_f=%d sites=%d problems=%d' % (
        len(changed), sum(len(v) for v in changed.values()), nhit, len(problems)))

    if '--dry' in sys.argv:
        return
    if problems:
        print('REFUSE: 校验未通过')
        return
    if not os.path.exists(os.path.dirname(BAK)):
        os.makedirs(os.path.dirname(BAK))
    if not os.path.exists(BAK):
        shutil.copy2(DB, BAK)
    for tid, d in changed.items():
        for f, (_, nv) in d.items():
            byid[tid][f] = nv
    txt = json.dumps(data, ensure_ascii=False, indent=2)
    with open(DB, 'w', encoding='utf-8', newline='\r\n') as fh:
        fh.write(txt)
    print('APPLIED')


if __name__ == '__main__':
    main()
