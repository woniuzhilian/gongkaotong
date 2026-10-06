import pymupdf, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
d = pymupdf.open(u'题目和答案pdf/公共基础分类版真题详解（13~24）_题目.pdf')
t = d[150].get_text()
i = t.find('2020-66')
print(repr(t[max(0,i-8):i+14]))
allm = re.findall(r'【[^】]{1,12}】', ' '.join(d[p].get_text() for p in range(148,153)))
print('markers sample', allm[:12], 'count', len(allm))
