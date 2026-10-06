# -*- coding: utf-8 -*-
import json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
PATH = r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
qs = json.load(open(PATH, encoding='utf-8'))
FIELDS=['question','A','B','C','D','analysis']

# collect every backslash control-word to find malformed ones
cw = collections.Counter()
for q in qs:
    for f in FIELDS:
        for m in re.finditer(r'\\[A-Za-z]+', str(q.get(f,''))):
            cw[m.group(0)]+=1
print("=== control words by freq ===")
for k,v in sorted(cw.items(), key=lambda x:-x[1]):
    print(f"  {k:20} {v}")

# suspicious multi-letter units glued after \cdot / \times
glue = collections.Counter()
for q in qs:
    for f in FIELDS:
        for m in re.finditer(r'\\(cdot|times|approx|leq|geq)([A-Za-z])', str(q.get(f,''))):
            glue[m.group(0)]+=1
print("\n=== \\cdotX / \\timesX glued ===")
for k,v in sorted(glue.items(), key=lambda x:-x[1]):
    print(f"  {k:14} {v}")
