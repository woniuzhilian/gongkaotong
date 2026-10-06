# -*- coding: utf-8 -*-
import re, os
O=r"C:\Users\Administrator\.qclaw\workspace\pdftxt"
def blocks(fn):
    txt=open(os.path.join(O,fn),encoding="utf-8").read()
    txt=re.sub(r"\n===== PAGE \d+ =====\n","\n",txt)
    parts=re.split(r"(【\d{4}(?:补)?-\d+】)",txt)
    res=[]
    for i in range(1,len(parts),2):
        res.append((parts[i],parts[i+1]))
    return res
import sys
sys.stdout.reconfigure(encoding="utf-8")
bq=blocks("pubQ.txt"); ba=blocks("pubA.txt")
print("pubQ blocks",len(bq),"pubA blocks",len(ba))
out=open(os.path.join(O,"blocks.txt"),"w",encoding="utf-8")
for tag,body in bq:
    out.write("@@@@ "+tag+"\n"+body.strip()+"\n\n")
out.close()
out=open(os.path.join(O,"blocksA.txt"),"w",encoding="utf-8")
for tag,body in ba:
    out.write("@@@@ "+tag+"\n"+body.strip()+"\n\n")
out.close()
print("ok")
