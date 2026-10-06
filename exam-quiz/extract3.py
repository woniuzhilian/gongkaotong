import pymupdf, io, re
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUBQ=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
doc=pymupdf.open(PUBQ)
full=[]
for p in range(doc.page_count):
    full.append("\n<<<PAGE %d>>>\n"%p + doc[p].get_text())
doc.close()
txt="".join(full)
mark=re.compile(r"【\s*(\d{4})\s*(补)?\s*-\s*(\d{1,3})\s*】")
ms=list(mark.finditer(txt))
want={"2018-68","2018-69","2019-67","2021-65","2022-90","2021-90","2019-59","2020-64","2023-92"}
out=[]
for i,m in enumerate(ms):
    key="%s%s-%s"%(m.group(1),"补" if m.group(2) else "",m.group(3))
    if key in want:
        end=ms[i+1].start() if i+1<len(ms) else m.start()+900
        out.append("@@@ %s\n%s"%(key, txt[m.start():end].strip()))
io.open(r"C:\Users\Administrator\.qclaw\workspace\blocks3.txt","w",encoding="utf-8").write("\n\n".join(out))
print("found",len(out))
