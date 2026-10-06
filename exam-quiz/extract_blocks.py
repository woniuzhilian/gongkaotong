import pymupdf, io, re
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
doc=pymupdf.open(PUBQ)
full=[]
for p in range(doc.page_count):
    full.append(("\n<<<PAGE %d>>>\n"%p)+doc[p].get_text())
doc.close()
txt="".join(full)
mark=re.compile(r"【(\d{4}(?:补)?)-(\d{1,3})】")
ms=list(mark.finditer(txt))
out=[]
for i,m in enumerate(ms):
    blk=txt[m.start(): ms[i+1].start() if i+1<len(ms) else m.start()+1500]
    out.append("@@@ 【%s-%s】\n%s"%(m.group(1),m.group(2),blk.strip()))
io.open(r"C:\Users\Administrator\.qclaw\workspace\blocks_pub.txt","w",encoding="utf-8").write("\n\n".join(out))
print("markers",len(ms))
