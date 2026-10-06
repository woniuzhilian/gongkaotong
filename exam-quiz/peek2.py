import os, re, pymupdf
ROOT=os.path.dirname(os.path.abspath(__file__)); P=os.path.join(ROOT,'题目和答案pdf')
MARK=re.compile(r'【\s*(\d{4})\s*(补)?\s*[-–]\s*(\d+)\s*】')
doc=pymupdf.open(os.path.join(P,'公共基础分类版真题详解（13~24）_题目.pdf'))
log=open(os.path.join(ROOT,'_peek2.txt'),'w',encoding='utf-8')
def segs(pno):
    pg=doc[pno]; blocks=[b for b in pg.get_text('blocks') if b[4].strip()]; ms=[]
    for b in blocks:
        m=MARK.search(b[4])
        if m: ms.append((b[1], m.group(1)+('补' if m.group(2) else '')+'-'+str(int(m.group(3)))))
    ms.sort()
    out=[]
    for i,(y,k) in enumerate(ms):
        y1=ms[i+1][0] if i+1<len(ms) else pg.rect.y1
        txt=''.join(b[4] for b in blocks if y-1<=b[1]<y1-1)
        out.append((k,y,y1,re.sub(r'\s+','',txt)))
    return out,pg
for pno, after in [(24,'2021-17'),(24,'2023-18'),(23,'2017-17')]:
    s,pg=segs(pno)
    i=[j for j,x in enumerate(s) if x[0]==after][0]
    for k,y,y1,txt in s[i:i+2]:
        print('=== p%d %s y(%d,%d)\n%s\n'%(pno,k,y,y1,txt[:300]),file=log)
        pix=pg.get_pixmap(clip=pymupdf.Rect(60,max(0,y-3),pg.rect.x1-20,min(pg.rect.y1,y1-3)),dpi=200)
        fn='n_%s_p%d.png'%(k.replace('-','_'),pno); pix.save(os.path.join(ROOT,'_t1',fn))
        print('   ->',fn,pix.width,pix.height,file=log)
doc.close(); log.close(); print('ok')
