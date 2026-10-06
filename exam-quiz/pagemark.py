# -*- coding: utf-8 -*-
import re, os, sys
sys.stdout.reconfigure(encoding="utf-8")
f=r"C:\Users\Administrator\.qclaw\workspace\pdftxt\pubQ.txt"
txt=open(f,encoding="utf-8").read()
pages=re.split(r"\n===== PAGE (\d+) =====\n",txt)
# pages: [pre, num, body, num, body...]
marks={}
for i in range(1,len(pages),2):
    n=int(pages[i]); body=pages[i+1]
    for m in re.findall(r"【(\d{4}(?:补)?-\d+)】",body):
        marks[m]=n
keys=["2017-89","2018-67","2018-69","2018-89","2020-94","2021-93","2021-94","2022-94","2023-94","2018-68","2022补-68","2022补-81","2022-81","2022-91","2019-94","2019-67","2019-70","2020-65","2021-65","2021-66","2021-69","2021-70","2023-63","2023-64","2016-67"]
for k in keys:
    print(k,"-> page",marks.get(k,"?"))
