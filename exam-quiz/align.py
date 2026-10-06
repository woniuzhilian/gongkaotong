# -*- coding: utf-8 -*-
import sys, json, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')
qs=json.load(open(r'E:\应用程序开发\刷题\exam-quiz\src\data\questions.json',encoding='utf-8'))
p=r"E:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf"
d=pymupdf.open(p)
# concat all text with markers, then locate
full=[]
for i in range(len(d)):
    full.append((i+1, d[i].get_text()))
def locate(sub):
    for pg,t in full:
        pos=t.find(sub)
        if pos>=0:
            # nearest preceding marker
            pre=list(re.finditer(r'【(\d{4}(?:补)?-\d+)】', t[:pos]))
            mk=pre[-1].group(1) if pre else None
            return pg, mk
    return None,None
tests={447:'AC+DC+ADC', 928:'ABC+AD+BD+CD', 813:'运算放大器输出电压的极限值', 932:'输出电压波形为', 658:'四种材料的应力', 306:'剪力图和弯矩图如图示', 538:'变截面杆', 546:'单元体的应力状态', 568:'数字信号F=A+B', 669:'四根细长', 693:'能够完成加法运算', 784:'整块材料', 904:'挠曲线大致形状', 908:'抗弯刚度EI相同', 1040:'等效电路为', 1050:'的波形', 1053:'输出电压波形', 1147:'平面应力状态', 1160:'等效电流源模型', 1262:'静矩', 1292:'小信号模型', 447+100000:'x'}
for qid,sub in tests.items():
    if qid>100000: continue
    pg,mk=locate(sub)
    q=qs[[x['id'] for x in qs].index(qid)]
    print(f"id{qid} json={q['year']}-{q['yearQnum']} {q['smallSubject'][:8]:8} | pdf page={pg} marker={mk} | sub={sub[:14]}")
