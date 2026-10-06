# -*- coding: utf-8 -*-
import zipfile, io, re, os
Z=r"E:\应用程序开发\刷题\题目配图_全部354题.zip"
z=zipfile.ZipFile(Z)
names=z.namelist()
ids=[306,448,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,2002]
out=["total entries: %d"%len(names)]
for i in ids:
    pref="id%d_"%i
    hit=[n for n in names if os.path.basename(n).lower().startswith(pref)]
    out.append("id=%d -> %s"%(i, hit))
# also list a few examples of good option sets
out.append("--- sample names ---")
for n in names[:40]:
    out.append(n)
io.open(r"C:\Users\Administrator\.qclaw\workspace\zip_names.txt","w",encoding="utf-8").write("\n".join(out))
print("done")
