# -*- coding: utf-8 -*-
"""T3 符号错映射修复。用法: py t3_apply.py --dry | py t3_apply.py"""
import os, re, sys, json, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
BAK = os.path.join(ROOT, '_fix_backup', 'questions_BEFORE_T3.json')
FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis']
B = chr(92)

# ---- 1) 跨题全文替换：PDF 提取把 sigma/epsilon 错映射成变体字形 ----
GLOBAL = [
    (B + 'varsigma', B + 'sigma'),
    (B + 'epsilon', B + 'varepsilon'),
]

# ---- 2) 跨题替换：[ ] 被错映射成 , 和 - ----
PI = B + 'pi'
BRACK = [
    (',-' + PI + ',' + PI + '-', '[-' + PI + ',' + PI + ']'),
    ('(-' + PI + ',' + PI + '-', '(-' + PI + ',' + PI + ']'),
    (',' + B + 'sigma -', '[' + B + 'sigma]'),
    (',' + B + 'sigma-', '[' + B + 'sigma]'),
    (',' + B + 'tau -', '[' + B + 'tau]'),
    (',' + B + 'tau-', '[' + B + 'tau]'),
]
# ---- 3) 限定题号的替换 ----
SCOPED = [
    ({60}, ',F-', '[F]'),
    ({534}, 'kN$' + B + 'cdots$2/m', 'kN$' + B + 'cdot s^{2}$/m'),
    ({750, 991}, B + 'cdots^{1}', B + 'cdot s^{-1}'),
]

# ---- 4) 整字段重写（已按原书裁图逐字核对） ----
OV = {}


def setf(tid, **kw):
    OV.setdefault(tid, {}).update(kw)


# 2013-39 原书作 Eθ(Fe3+/Fe)，用的是 θ 而非标准态符 ⊖
setf(39,
     question=r"已知$E^{\theta}(\mathrm{Fe^{3+}}/\mathrm{Fe^{2+}})=0.771\mathrm{V}$，$E^{\theta}(\mathrm{Fe^{2+}}/\mathrm{Fe})=-0.44\mathrm{V}$，则$E^{\theta}(\mathrm{Fe^{3+}}/\mathrm{Fe})$等于：（　　）。",
     analysis=r"利用标准电极电势图计算某电对的标准电极电势。$\mathrm{Fe^{3+}}\xrightarrow{0.771}\mathrm{Fe^{2+}}\xrightarrow{-0.44}\mathrm{Fe}$，依据标准电极电势的计算公式：$E^{\theta}(\mathrm{Fe^{3+}}/\mathrm{Fe})=\frac{1\times0.771+2\times(-0.44)}{3}=-0.036\mathrm{V}$")

# 2013-43 解析整段重排
setf(43,
     analysis=r"浓度对电极电势的影响。负极半反应是$\mathrm{Ag}+\mathrm{Cl}^{-}-\mathrm{e}=\mathrm{AgCl}$，$E_{\mathrm{AgCl/Ag}}=E_{\mathrm{AgCl/Ag}}^{\ominus}+\frac{0.059}{1}\lg\frac{1}{[\mathrm{Cl}^{-}]}$，随着$\mathrm{NaCl}$的加入，$[\mathrm{Cl}^{-}]$增加，$E_{\mathrm{AgCl/Ag}}$减小。原电池的电动势$E=E_{(+)}-E_{(-)}$，所以原电池电动势增加。")

# 2014-41 解析：原库把 Cu 错认成 Co，整段重排
setf(160,
     analysis=r"形成难溶电解质沉淀对电极电势的影响。未通入硫化氢前，铜半电池的反应是正极反应$\mathrm{Cu}^{2+}+2\mathrm{e}=\mathrm{Cu}$，$E_{\mathrm{Cu^{2+}/Cu}}=E_{\mathrm{Cu^{2+}/Cu}}^{\ominus}+\frac{0.059}{2}\lg[\mathrm{Cu}^{2+}]$，通入硫化氢之后，$\mathrm{Cu}^{2+}$与$\mathrm{H_2S}$生成$\mathrm{CuS}$沉淀，$\mathrm{Cu}^{2+}$浓度减小。氧化型物质形成难溶电解质沉淀时，标准电极电势减小，即$E_{\mathrm{CuS/Cu}}^{\ominus}<E_{\mathrm{Cu^{2+}/Cu}}^{\ominus}$，即$E_{(+)}$减小，因原电池的电动势$E=E_{(+)}-E_{(-)}$，所以原电池电动势减小。")

# 2014-42 解析
setf(161,
     analysis=r"电解氧化还原半反应的书写，电极电势的应用。电解时阴极上总是发生还原反应。$\mathrm{NaCl}$水溶液中存在的离子有$\mathrm{Na}^{+}$、$\mathrm{H}^{+}$、$\mathrm{Cl}^{-}$、$\mathrm{OH}^{-}$，电解反应发生时溶液中可以发生还原反应的离子有$\mathrm{Na}^{+}$和$\mathrm{H}^{+}$：依据它们的标准电极电势，$E_{\mathrm{H^{+}/H_2}}^{\ominus}=0>E_{\mathrm{Na^{+}/Na}}^{\ominus}=-2.71$，$\mathrm{H}^{+}$比$\mathrm{Na}^{+}$更易被还原。所以阴极反应是$2\mathrm{H}^{+}+2\mathrm{e}=\mathrm{H_2}\uparrow$")

# 2015-39 解析：原书为 ΔrHm⊖<0
setf(42,
     analysis=r"平衡的移动。依据平衡移动吕·查德里原理，对于有气态物质参加的化学平衡体系，要使平衡向气体分子总数减少的方向移动，需增加总压力。$\Delta_{\mathrm{r}}H_{\mathrm{m}}^{\ominus}<0$，反应是放热反应。降温，平衡向放热反应方向移动，所以应该选C。")

# 2016-41 解析：原书解析止于四个半反应，尾部的能斯特公式是相邻题串入
setf(280,
     analysis=r"半反应的书写与电极电势的计算（能斯特方程）。根据电对写出半反应，可发现仅有答案D的电极电势与$\mathrm{H}^{+}$浓度有关。A 半反应为$\mathrm{Zn}^{2+}\rightarrow\mathrm{Zn}$；B 半反应为$\mathrm{Br_2}\rightarrow\mathrm{Br}^{-}$；C 半反应为$\mathrm{AgI}\rightarrow\mathrm{Ag}+\mathrm{I}^{-}$；D 半反应为$\mathrm{MnO_4}^{-}+8\mathrm{H}^{+}\rightarrow\mathrm{Mn}^{2+}+4\mathrm{H_2O}$")

# 2013-60 选项丢了成对 $
setf(60,
     A=r"$[F]=A[\sigma]$",
     B=r"$[F]=2A[\sigma]$",
     C=r"$[F]=3A[\sigma]$",
     D=r"$[F]=4A[\sigma]$")

# 2016-39 题干的标准态符号
setf(278,
     question=r"已知$K_b^{\ominus}(\mathrm{NH_3})=1.8\times10^{-5}$。$0.10\mathrm{mol}\cdot\mathrm{dm}^{-3}$氨水溶液的pH值为：（　　）。")

# 2020-31 解析里的单位
setf(750,
     analysis=r"波动方程。$T=1/\nu=1/2000\mathrm{s}$，波速$u=\lambda/T=\lambda\nu=0.2\times2000=400\mathrm{m}\cdot\mathrm{s}^{-1}$")


def apply_all(txt):
    hits = []
    for old, new in GLOBAL + BRACK:
        if old in txt:
            hits.append(old)
            txt = txt.replace(old, new)
    return txt, hits


def apply_scoped(tid, txt):
    hits = []
    for ids, old, new in SCOPED:
        if tid in ids and old in txt:
            hits.append(old)
            txt = txt.replace(old, new)
    return txt, hits


def check(tid, fld, old, v):
    bad = []
    if v.count('$') % 2:
        bad.append('odd-$')
    if '$$' in v:
        bad.append('adj-$$')
    if v.endswith(B) and not old.endswith(B):
        bad.append('trailing-backslash')
    return ['%s/%s: %s' % (tid, fld, x) for x in bad]


def main():
    data = json.load(open(DB, encoding='utf-8'))
    byid = {q['id']: q for q in data}
    problems, changed = [], {}

    for q in data:
        tid = q['id']
        for f in FIELDS:
            v = q.get(f)
            if not isinstance(v, str) or not v:
                continue
            nv, _ = apply_all(v)
            nv, _ = apply_scoped(tid, nv)
            if tid in OV and f in OV[tid]:
                nv = OV[tid][f]
            if nv != v:
                problems += check(tid, f, v, nv)
                changed.setdefault(tid, {})[f] = (v, nv)

    # 残留检查：这些错映射字形不应再出现在任何字段
    for q in data:
        tid = q['id']
        for f in FIELDS:
            v = q.get(f)
            if not isinstance(v, str):
                continue
            nv = changed.get(tid, {}).get(f, (None, v))[1]
            for tok in (B + 'varsigma', B + 'epsilon', B + 'Theta', B + 'cdots^{1}',
                        'kN$' + B + 'cdots$'):
                if tok in nv:
                    problems.append('RESIDUAL %s/%s: %s' % (tid, f, tok))

    for tid in OV:
        for f in OV[tid]:
            if f not in changed.get(tid, {}):
                problems.append('OVERRIDE-NOOP %s/%s' % (tid, f))

    rep = []
    rep.append('受影响题目数=%d  受影响字段数=%d' % (len(changed), sum(len(v) for v in changed.values())))
    rep.append('校验问题数=%d' % len(problems))
    for p in problems:
        rep.append('  !! ' + p)
    for tid in sorted(changed):
        rep.append('---- id=%d' % tid)
        for f, (a, b) in changed[tid].items():
            rep.append('  [%s] - %s' % (f, a))
            rep.append('  [%s] + %s' % (f, b))
    out = os.path.join(ROOT, '_t3_apply.txt')
    with open(out, 'w', encoding='utf-8', newline='\r\n') as fh:
        fh.write('\n'.join(rep))
    json.dump({str(k): {f: v[1] for f, v in d.items()} for k, d in changed.items()},
              open(os.path.join(ROOT, '_t3_new.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('changed_q=%d changed_f=%d problems=%d' % (len(changed), sum(len(v) for v in changed.values()), len(problems)))

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
