# -*- coding: utf-8 -*-
import json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
q=json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))
pub=[x for x in q if x['bigSubject']=='公共基础']
# per year, list missing yearQnum in 1..expected
expect={'2013':120,'2014':120,'2016':120,'2017':120,'2018':120,'2019':120,'2020':120,'2021':120,'2022':120,'2022补':120,'2023':120,'2024':120}
for y,e in expect.items():
    nums=sorted(x['yearQnum'] for x in pub if x['year']==y)
    missing=[n for n in range(1,e+1) if n not in nums]
    extra=[n for n in nums if n>e]
    if missing or extra or len(nums)!=e:
        print(f"{y}: count={len(nums)} missing={missing} extra={extra}")
print("公共基础 2013 check done")
# 专业基础
pro=[x for x in q if x['bigSubject']=='专业基础']
for y in ['2016','2017','2018','2019','2020','2021','2022','2022补','2023','2024']:
    nums=sorted(x['yearQnum'] for x in pro if x['year']==y)
    e=56 if y=='2024' else 60
    missing=[n for n in range(1,e+1) if n not in nums]
    print(f"专业 {y}: count={len(nums)} max={max(nums) if nums else None} missing={missing}")
