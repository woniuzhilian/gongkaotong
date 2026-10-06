# -*- coding: utf-8 -*-
import json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

PATH = r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
qs = json.load(open(PATH, encoding='utf-8'))

def scan(name, pred):
    hits = [q['id'] for q in qs if pred(q)]
    print(f"[{name}] count={len(hits)}")
    print("   ", hits[:80])
    print()
    return hits

# 特殊符号/乱码
scan("反斜杠 LaTeX 泄漏(\\)", lambda q: any('\\' in str(q.get(f,'')) for f in ['question','A','B','C','D','analysis']))
scan("美元符号($)", lambda q: any('$' in str(q.get(f,'')) for f in ['question','A','B','C','D','analysis']))
scan("花括号泄漏{}", lambda q: any(('{' in str(q.get(f,'')) or '}' in str(q.get(f,''))) for f in ['question','A','B','C','D']))
scan("图片标记", lambda q: any('![' in str(q.get(f,'')) or '<img' in str(q.get(f,'')) for f in ['question','A','B','C','D','analysis']))
scan("HTML标签", lambda q: any(re.search(r'<[a-zA-Z/][^>]*>', str(q.get(f,''))) for f in ['question','A','B','C','D','analysis']))
scan("Unicode替换字符U+FFFD", lambda q: any('\ufffd' in str(q.get(f,'')) for f in ['question','A','B','C','D','analysis']))
scan("下划线表示下标", lambda q: any(re.search(r'[A-Za-z]\d*_\{?[0-9A-Za-z]', str(q.get(f,''))) for f in ['question','A','B','C','D']))
scan("方括号引用[", lambda q: any('[' in str(q.get(f,'')) or ']' in str(q.get(f,'')) for f in ['question','A','B','C','D','analysis']))
scan("字符^", lambda q: any('^' in str(q.get(f,'')) for f in ['question','A','B','C','D']))

# 疑似解析过短（不完整）
short = [(q['id'], len(q.get('analysis',''))) for q in qs if len(q.get('analysis','').strip()) < 8]
print("[解析过短<8]", len(short), short[:60])
print()
shortq = [(q['id'], len(q.get('question','')), q.get('question','')) for q in qs if len(q.get('question','').strip()) < 10]
print("[题干过短<10]", len(shortq))
for s in shortq[:60]: print("   ", s)
