# -*- coding: utf-8 -*-
import os, io, re
D=r"E:\应用程序开发\刷题\exam-quiz\public\images"
files=os.listdir(D)
groups={}
# pattern idNNN_YYYY_NN[_sub][.ext]
pat=re.compile(r"^id(\d+)_")
byname={}
for f in files:
    byname.setdefault(f.lower(),f)
# For broken ids, list all files whose stem starts with id<id>_  (same question)
ids=[306,448,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,2002]
out=[]
for i in ids:
    pref="id%d_"%i
    hit=sorted([f for f in files if f.lower().startswith(pref)])
    out.append("id=%d -> %s"%(i,hit))
# Also: list ALL files that look like option-subfigs (ending _2.._6) referenced by good examples
io.open(r"C:\Users\Administrator\.qclaw\workspace\img_by_id.txt","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
