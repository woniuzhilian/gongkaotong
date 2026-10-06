# -*- coding: utf-8 -*-
"""修复题目中"LaTeX 命令被粘连"的显示错误：\cdotm -> \cdot m, \sqrtx -> \sqrt x 等。
仅处理 $...$ 数学段内的反斜杠命令。用最长有效前缀切分。
"""
import json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

PATH = r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
FIELDS = ['question','A','B','C','D','analysis']

# KaTeX 支持的完整命令白名单（含各长度前缀需覆盖）
VALID = set("""
times frac dfrac tfrac sqrt cdot cdots ldots vdots ddots alpha beta gamma delta epsilon varepsilon
zeta eta theta vartheta iota kappa lambda mu nu xi pi varpi rho varrho sigma varsigma tau upsilon phi
varphi chi psi omega varkappa
Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega
infty partial nabla sum prod int iint iiint oint lim to rightarrow leftarrow leftrightarrow Rightarrow
Leftarrow Leftrightarrow Longrightarrow Longleftarrow Longleftrightarrow
rightleftharpoons uparrow downarrow updownarrow nearrow searrow swarrow nwarrow hookrightarrow hookleftarrow
leq geq neq approx equiv sim simeq propto pm mp div ast star circ bullet cap cup subset supset subseteq
supseteq in notin emptyset forall exists neg land lor angle triangle square prime
sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh log ln lg exp max min det deg
mathrm mathbf mathit mathcal mathbb mathfrak mathsf mathtt text begin end left right middle
bar hat vec dot ddot tilde widehat widetilde overline underline overbrace underbrace
ominus oplus otimes oslash bigoplus bigotimes bigodot
therefore because parallel perp mid ll gg sim
lbrace rbrace lbrack rbrack langle rangle lvert rvert
space quad qquad limits nolimits
""".split())

def split_word(word):
    out = []
    i = 0
    while i < len(word):
        matched = None
        for L in range(len(word)-i, 0, -1):
            if word[i:i+L] in VALID:
                matched = word[i:i+L]; break
        if matched:
            out.append(matched); i += len(matched)
        else:
            # 无法匹配的字母原样保留（会作为普通标识符，渲染为斜体变量）
            out.append(word[i]); i += 1
    return out

def fix_spans(text):
    if not text or '$' not in text: return text, 0
    n = 0
    def repl(m):
        nonlocal n
        inner = m.group(1)
        def tok(mm):
            nonlocal n
            word = mm.group(1)
            parts = split_word(word)
            joined = ' '.join('\\'+p for p in parts)
            if joined != '\\'+word:
                n += 1
            return joined
        # 只匹配未被另一个反斜杠转义的命令
        new = re.sub(r'(?<!\\)\\([A-Za-z]+)', tok, inner)
        return '$' + new + '$'
    res = re.sub(r'\$([^$]*)\$', repl, text)
    return res, n

qs = json.load(open(PATH, encoding='utf-8'))
tot = 0
perfield = collections.Counter()
for q in qs:
    for f in FIELDS:
        v = q.get(f, '')
        if isinstance(v, str):
            nv, n = fix_spans(v)
            if n:
                q[f] = nv; tot += n; perfield[f]+=n

json.dump(qs, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"拆分修复 token 数: {tot}")
print("按字段:", dict(perfield))
