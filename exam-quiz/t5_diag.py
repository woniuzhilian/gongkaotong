# -*- coding: utf-8 -*-
"""T5 诊断：为什么大量 DB 符号点在原书键表里找不到"""
import io, re, os, collections, json

ROOT = os.path.dirname(os.path.abspath(__file__))
txt = io.open(os.path.join(ROOT, '_t5_prop.txt'), encoding='utf-8').read()
blocks = re.split(r'\n(?=##### id=)', txt)
out = io.open(os.path.join(ROOT, '_t5_diag.txt'), 'w', encoding='utf-8')
st = collections.Counter()
rows = []
for b in blocks:
    m = re.match(r'##### id=(\d+) 书证点=(\d+) 可用键=(\d+)', b)
    if not m:
        continue
    tid, nsite, nkey = int(m.group(1)), int(m.group(2)), int(m.group(3))
    dbs = re.findall(r'^\s+DB @(\d+) (.) k=(\S+)\s+nb=(\d+) na=(\d+) inbook=(\d)', b, re.M)
    if not dbs:
        continue
    st['题'] += 1
    st['点'] += len(dbs)
    for k in re.findall(r'inbook=0', b):
        st['未命中'] += 1
    rows.append((tid, nsite, nkey, len(dbs)))
    if nkey == 0:
        st['整题无键'] += 1
rows.sort(key=lambda r: (r[1] - r[3], r[1]), reverse=True)
for r in rows[:40]:
    out.write('id=%d 书证点=%d 可用键=%d 未命中=%d\n' % (r[0], r[1], r[2], r[1] - r[3]))
out.write('\n'.join('%s=%d' % (k, v) for k, v in sorted(st.items())) + '\n')
# 打印几个未命中点的书证侧上下文
out.write('\n' + '=' * 60 + '\n')
for tid in [int(x) for x in re.findall(r'^id=(\d+)', '\n'.join(str(r[0]) for r in rows[:14]), re.M)]:
    blk = [b for b in blocks if b.startswith('##### id=%d ' % tid)]
    if blk:
        out.write('\n'.join(blk[0].split('\n')[:34]) + '\n\n')
out.close()
print(' | '.join('%s=%d' % (k, v) for k, v in sorted(st.items())))
