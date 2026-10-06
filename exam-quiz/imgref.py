# -*- coding: utf-8 -*-
import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
P=r"E:\应用程序开发\刷题\exam-quiz\src\data\questions.json"
IMG=r"E:\应用程序开发\刷题\exam-quiz\public\images"
Q=json.load(open(P,encoding='utf-8'))
IDS=[306,447,448,538,546,568,658,666,669,693,784,813,904,908,928,932,1040,1050,1053,1147,1160,1262,1292,1588,1626,2002,94,451,560,561,682,695,1151,1155,1218,1391,1680,1932]
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\imgref.txt","w",encoding="utf-8")
for i in IDS:
    q=next(x for x in Q if x['id']==i)
    refs=re.findall(r'src="([^"]+)"', q['question']+q['A']+q['B']+q['C']+q['D'])
    OUT.write(f"\nid{i}:")
    for r in refs:
        rel=r.split('/images/')[-1]
        full=os.path.join(IMG,rel.replace('/',os.sep))
        OUT.write(f"\n   {'OK ' if os.path.exists(full) else 'MISS'} {r}")
OUT.close(); print(open(r"C:\Users\Administrator\.qclaw\workspace\imgref.txt",encoding="utf-8").read())
