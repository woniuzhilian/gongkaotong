# -*- coding: utf-8 -*-
import re, os, sys
sys.stdout.reconfigure(encoding="utf-8")
O=r"C:\Users\Administrator\.qclaw\workspace\pdftxt"
def blocks(fn):
    txt=open(os.path.join(O,fn),encoding="utf-8").read()
    txt=re.sub(r"\n===== PAGE \d+ =====\n","\n",txt)
    parts=re.split(r"(【\d{4}(?:补)?-\d+】)",txt)
    res={}
    for i in range(1,len(parts),2):
        res[parts[i]]=parts[i+1].strip()
    return res
bq=blocks("pubQ.txt"); ba=blocks("pubA.txt")
keys=["2016-67","2017-90","2017-91","2017-92","2018-60","2018-69","2018-90","2018-91","2019-59","2019-67","2019-70","2019-94","2020-65","2020-94","2021-65","2021-66","2021-69","2021-70","2021-89","2021-90","2021-93","2021-94","2022-81","2022-91","2022-94","2018-68","2022补-68","2023-64","2023-94","2022补-81"]
out=open(os.path.join(O,"sel.txt"),"w",encoding="utf-8")
for k in keys:
    t="【"+k+"】"
    out.write("\n\n########## "+t+"  QUESTION ##########\n")
    out.write(bq.get(t,"(none)")[:1400])
    out.write("\n---------- ANSWER ----------\n")
    out.write(ba.get(t,"(none)")[:1400])
out.close()
print("done")
