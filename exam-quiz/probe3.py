# -*- coding: utf-8 -*-
import io, re, os
import pymupdf
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ=os.path.join(BASE,"公共基础分类版真题详解（13~24）_题目.pdf")
PROQ=os.path.join(BASE,"岩土专业基础分类真题解析（16~24）_题目.pdf")
# stem page per id (0-based) from markers.py
STEM={306:146,448:231,546:161,568:232,658:127,666:149,669:165,693:242,784:150,813:242,
 904:151,908:163,928:223,932:243,1040:200,1050:224,1053:244,1147:158,1160:202,1262:130,1292:245}
labelpat=re.compile(r"[(（]\s*([A-Da-d])\s*[)）]")
out=[]
doc=pymupdf.open(PUBQ)
for qid,sp in STEM.items():
    for p in range(max(0,sp-1), min(doc.page_count,sp+2)):
        pg=doc[p]
        words=pg.get_text("words")
        labels=[(m.group(1).upper(),round(w[0],1),round(w[1],1)) for w in words for m in [labelpat.match(w[4])] if m]
        imgs=[]
        for im in pg.get_images(full=True):
            try:
                r=pg.get_image_bbox(im)
                imgs.append((round(r.x0,1),round(r.y0,1),round(r.x1,1),round(r.y1,1)))
            except: pass
        drw=len(pg.get_drawings())
        out.append("id=%s p=%d imgs=%s"%(qid,p,imgs))
        out.append("     labels=%s drawings=%d"%(labels,drw))
doc.close()
io.open(r"C:\Users\Administrator\.qclaw\workspace\probe3.txt","w",encoding="utf-8").write("\n".join(out))
print("done")
