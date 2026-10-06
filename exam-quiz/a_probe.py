import pymupdf, os, re, json

DOCS = {
    'pub': os.path.join('题目和答案pdf', '公共基础分类版真题详解（13~24）_答案解析.pdf'),
    'pro': os.path.join('题目和答案pdf', '岩土专业基础分类真题解析（16~24）_答案解析.pdf'),
}
IDS = [8, 40, 60, 61, 131, 136, 143, 243, 254, 256, 278, 371, 375, 376, 380, 382, 383, 486, 496, 501, 552, 613, 615, 623, 625, 721, 731, 735, 737, 779, 812, 855, 856, 863, 971, 987, 993, 1001, 1011, 1012, 1014, 1025, 1028, 1093, 1095, 1102, 1103, 1122, 1140, 1147, 1149, 1214, 1217, 1223, 1329, 1333, 1336, 1343, 1344, 1347, 1372, 1380, 1381, 1467, 1524, 1583, 1645, 1827, 1828, 1844]

data = json.load(open(os.path.join('exam-quiz', 'src', 'data', 'questions.json'), encoding='utf-8'))
byid = {q['id']: q for q in data}
out = []
out.append('本批 %d 题' % len(IDS))
for q in data:
    pass
grp = {}
for i in IDS:
    q = byid[i]
    grp.setdefault(q['bigSubject'], []).append(i)
for k, v in grp.items():
    out.append('bigSubject=%r 题数=%d  ids=%s' % (k, len(v), ','.join(map(str, v[:8])) + '...'))
for tag, p in DOCS.items():
    d = pymupdf.open(p)
    out.append('%s %s pages=%d' % (tag, os.path.basename(p), d.page_count))
    for pno in (0, 1, 2):
        t = d[pno].get_text()
        out.append('--- %s p%d (%d chars) ---' % (tag, pno, len(t)))
        out.append(t[:700])
open('_a_probe.txt', 'w', encoding='utf-8').write('\n'.join(out))
