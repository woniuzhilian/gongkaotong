import pymupdf, io, re
BASE=r"E:\应用程序开发\刷题\题目和答案pdf"
PUB=BASE+r"\公共基础分类版真题详解（13~24）_题目.pdf"
doc=pymupdf.open(PUB)
full=["\n<<<PAGE %d>>>\n"%p+doc[p].get_text() for p in range(doc.page_count)]
doc.close(); txt="".join(full)
mark=re.compile(r"【\s*(\d{4})\s*(补)?\s*-\s*(\d{1,3})\s*】")
ms=list(mark.finditer(txt))
want={"2021-94","2022-90","2020-93","2020-94","2020-95","2019-93","2019-94","2019-95","2021-89","2021-90","2021-91","2021-92","2021-93","2023-93","2023-94","2022补-80","2022补-81"}
out=[]
for i,m in enumerate(ms):
    key="%s%s-%s"%(m.group(1),"补" if m.group(2) else "",m.group(3))
    if key in want:
        end=ms[i+1].start() if i+1<len(ms) else m.start()+700
        out.append("@@@ %s\n%s"%(key,txt[m.start():end].strip()))
io.open(r"C:\Users\Administrator\.qclaw\workspace\blocks4.txt","w",encoding="utf-8").write("\n\n".join(out))
print("found",len(out))
