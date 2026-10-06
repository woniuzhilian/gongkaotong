# -*- coding: utf-8 -*-
import re, os, sys
sys.stdout.reconfigure(encoding="utf-8")
def marks(fn):
    f=r"C:\Users\Administrator\.qclaw\workspace\pdftxt\\"+fn
    txt=open(f,encoding="utf-8").read()
    pages=re.split(r"\n===== PAGE (\d+) =====\n",txt)
    m={}
    for i in range(1,len(pages),2):
        for mm in re.findall(r"【(\d{4}(?:补)?-\d+)】",pages[i+1]):
            m.setdefault(mm,int(pages[i]))
    return m
m=marks("pubQ.txt")
for k in ["2017-91","2018-91","2016-91","2019-94","2020-94","2021-94","2022-94","2023-94","2022-91","2022-81","2023-64","2021-66","2020-65","2019-70","2018-68","2021-70"]:
    print(k,m.get(k,"?"))
print("--- pro ---")
m2=marks("proQ.txt")
for k,pg in m2.items():
    print(k,pg)
