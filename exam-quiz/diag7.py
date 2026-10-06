# -*- coding: utf-8 -*-
import json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
PATH = r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
qs = json.load(open(PATH, encoding='utf-8'))
FIELDS=['question','A','B','C','D','analysis']

VALID = set("""
times frac dfrac tfrac sqrt cdot cdots ldots vdots ddots alpha beta gamma delta epsilon varepsilon
zeta eta theta vartheta iota kappa lambda mu nu xi pi varpi rho varrho sigma varsigma tau upsilon phi
varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega
infty partial nabla sum prod int iint iiint oint lim to rightarrow leftarrow leftrightarrow Rightarrow
Leftarrow Leftrightarrow rightleftharpoons uparrow downarrow updownarrow nearrow searrow swarrow nwarrow
leq geq neq approx equiv sim simeq propto pm mp div ast star circ bullet cap cup subset supset subseteq
supseteq in notin emptyset forall exists neg land lor angle triangle square prime infty
sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh log ln lg exp lim max min
mathrm mathbf mathit mathcal mathbb mathfrak mathsf mathtt text begin end left right middle
bar hat vec dot ddot tilde widehat widetilde overline underline overbrace underbrace
ominus oplus otimes oslash bigoplus bigotimes bigodot
therefore because parallel perp mid ll gg sim
lbrace rbrace lbrack rbrack langle rangle lvert rvert
space quad qquad
""".split())

mal = collections.Counter()
bad_q = collections.Counter()
for q in qs:
    for f in FIELDS:
        for m in re.finditer(r'\\([A-Za-z]+)', str(q.get(f,''))):
            w=m.group(1)
            if w not in VALID:
                mal['\\'+w]+=1
                bad_q[q['id']]+=1

print(f"malformed-token occurrences: {sum(mal.values())}, distinct={len(mal)}, affected questions={len(bad_q)}")
print("top 60:")
for k,v in mal.most_common(60):
    print(f"   {k:22} {v}")
print("\naffected qids sample:", sorted(bad_q)[:80])
