import os, re, pymupdf
ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, '题目和答案pdf')
MARK = re.compile(r'【\s*(\d{4})\s*(补)?\s*[-–]\s*(\d+)\s*】')
doc = pymupdf.open(os.path.join(P, '公共基础分类版真题详解（13~24）_题目.pdf'))
want = [('2021-16',10), ('2023-96',227), ('2021-17',24), ('2021-16',22)]
log = open(os.path.join(ROOT,'_peek.txt'),'w',encoding='utf-8')
for key, pno in want:
    pg = doc[pno]
    blocks=[b for b in pg.get_text('blocks') if b[4].strip()]
    ms=[]
    for b in blocks:
        m=MARK.search(b[4])
        if m: ms.append((b[1], m.group(1)+('补' if m.group(2) else '')+'-'+str(int(m.group(3)))))
    ms.sort()
    for i,(y,k) in enumerate(ms):
        if k!=key: continue
        y1 = ms[i+1][0] if i+1<len(ms) else pg.rect.y1
        txt=''.join(b[4] for b in blocks if y-1<=b[1]<y1-1)
        print('=== %s p%d y(%d,%d)\n%s\n' % (k,pno,y,y1,re.sub(r'\s+','',txt)[:400]), file=log)
        pix=pg.get_pixmap(clip=pymupdf.Rect(60,max(0,y-3),pg.rect.x1-20,min(pg.rect.y1,y1-3)),dpi=200)
        fn='p_%s_p%d_%s.png'%(k.replace('-','_'),pno,key.replace('-','_'))
        pix.save(os.path.join(ROOT,'_t1',fn))
        print('   ->',fn,pix.width,pix.height, file=log)
doc.close(); log.close(); print('ok')
