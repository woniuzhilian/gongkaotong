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
for k in ["2016-91","2017-91","2018-91","2017-89","2018-89","2022补-68","2022补-81","2022补-91"]:
    t="【"+k+"】"
    print("\n##########",t,"##########")
    print("[Q]",bq.get(t,"(none)")[:900])
    print("[A]",ba.get(t,"(none)")[:700])
