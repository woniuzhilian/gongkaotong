# -*- coding: utf-8 -*-
import io, re, os, json
import pymupdf

BASE = r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ = os.path.join(BASE, "公共基础分类版真题详解（13~24）_题目.pdf")
PROQ = os.path.join(BASE, "岩土专业基础分类真题解析（16~24）_题目.pdf")

# id -> (which_pdf, page_index)
PAGES = {
 306:("pub",146),548:("pub",231),
 448:("pub",231),546:("pub",161),568:("pub",232),658:("pub",127),666:("pub",149),
 669:("pub",165),693:("pub",242),784:("pub",150),813:("pub",242),904:("pub",151),
 908:("pub",163),928:("pub",223),932:("pub",243),1040:("pub",200),1050:("pub",224),
 1053:("pub",244),1147:("pub",158),1160:("pub",202),1262:("pub",130),1292:("pub",245),
}

labelpat = re.compile(r"[(（]\s*([A-Da-d])\s*[)）]")

out=[]
for qid,(kind,pi) in PAGES.items():
    path = PUBQ if kind=="pub" else PROQ
    doc=pymupdf.open(path)
    pg=doc[pi]
    H=pg.rect.height; W=pg.rect.width
    words=pg.get_text("words")  # x0,y0,x1,y1,word,block,line,wordno
    labels=[]
    for w in words:
        m=labelpat.match(w[4])
        if m:
            labels.append((m.group(1).upper(), round(w[0],1), round(w[1],1)))
    imgs=[(round(r.x0,1),round(r.y0,1),round(r.x1,1),round(r.y1,1)) for r in [pg.get_image_bbox(im) for im in pg.get_images(full=True)] if r]
    out.append("id=%s page=%d W=%.0f H=%.0f"%(qid,pi,W,H))
    out.append("  labels: %s"%labels)
    out.append("  images: %s"%imgs)
    doc.close()
io.open(r"C:\Users\Administrator\.qclaw\workspace\labels_imgs.txt","w",encoding="utf-8").write("\n".join(out))
print("done")
