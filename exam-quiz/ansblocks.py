import pymupdf, io, re
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBA=BASE+r"\公共基础分类版真题详解（13~24）_答案解析.pdf"
doc=pymupdf.open(PUBA)
full=[]
for p in range(doc.page_count):
    full.append("\n<<<PAGE %d>>>\n"%p + doc[p].get_text())
doc.close()
txt="".join(full)
mark=re.compile(r"【\s*(\d{4})\s*(补)?\s*-\s*(\d{1,3})\s*】")
ms=list(mark.finditer(txt))
want={"2019-59","2018-67","2018-68","2018-69","2019-67","2019-70","2019-94","2020-65","2020-94","2021-65","2021-66","2021-70","2021-90","2021-93","2022-81","2022-91","2022-94","2022补-68","2022补-81","2023-63","2023-64","2023-93","2023-94","2016-67","2017-89","2018-89","2021-69"}
out=[]
for i,m in enumerate(ms):
    key="%s%s-%s"%(m.group(1),"补" if m.group(2) else "",m.group(3))
    if key in want:
        end=ms[i+1].start() if i+1<len(ms) else m.start()+500
        out.append("@@@ %s\n%s"%(key, txt[m.start():end].strip()[:500]))
io.open(r"C:\Users\Administrator\.qclaw\workspace\ansblocks.txt","w",encoding="utf-8").write("\n\n".join(out))
print("found",len(out))
