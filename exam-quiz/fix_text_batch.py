# -*- coding: utf-8 -*-
import sys, os, json, shutil
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\exam-quiz\src\data"
P=os.path.join(D,"questions.json")
BAK=os.path.join(D,"questions_BACKUP_20260913_104530.json")
Q=json.load(open(BAK,encoding='utf-8'))   # latest good state (katex-fixed)
byid={q['id']:q for q in Q}
FIX={
 94:{"question":"图（A）所示电路中，复位信号$\\overline{R_D}$、信号A及时钟脉冲信号cp如图（B）所示，经分析可知，在第一个和第二个时钟脉冲的下降沿时刻，输出Q分别等于（　）。"},
 447:{"A":"C","B":"A+D+C","C":"AC+DC","D":"$\\overline{A}+\\overline{C}$"},
 451:{"question":"图（A）所示电路中，运算放大器输出电压的极限值$\\pm U_{OM}$。当输入电压$U_{c1}=1V$，$U_{c2}=2\\sin\\omega t\\,V$时，输出电压波形如图（B）所示，那么，如果将$U_{c1}$从1V调至1.5V，将会使输出端电压的（　）。"},
 538:{"question":"变截面杆AC受力如图。已知材料弹性模量为E，杆BC段的截面积为A，杆AB段的截面积为2A。杆C截面的轴向位移是（　）。<br><img src=\"/images/id705_2018_60_3.png\" style=\"max-width:100%;\">",
      "A":"$\\frac{FL}{2EA}$","B":"$\\frac{FL}{EA}$","C":"$\\frac{2FL}{EA}$","D":"$\\frac{3FL}{EA}$"},
 560:{"question":"对于图示电路，可以列写a、b、c、d四个结点KCL方程和①、②、③、④四个回路的KVL方程。为求出5个未知电流$I_1\\sim I_5$，正确的求解模型是（　）。",
      "answer":"C",
      "analysis":"根据支路电流法，三条及三条以上支路联结点是节点n=4，闭合电路中不含其他支路的回路称为网孔m=3。可以列写n-1个KCL方程和m个KVL方程。有电流源的电路，列写m-k个回路电压方程，其中k为电流源个数，本题k=1，且选择不包含电流源的回路列写电压方程。故n-1=4-1=3个KCL方程，m-k=3-1=2个KVL方程，且选择不包含电流源的回路列写电压方程，答案为C。"},
 561:{"question":"图（A）所示功率因数补偿电路中，$C=C_1$时得到相量图如图（B）所示，$C=C_2$时得到相量图如图（C）所示，那么（　）。"},
 658:{"question":"图示四种材料的应力—应变曲线中，强度最大的材料是（　）。<br><img src=\"/images/id706_2019_59_crop.png\" style=\"max-width:100%;\">"},
 682:{"question":"额定容量为20kV·A、额定电压为220V的某交流电源，有功功率为8kW、功率因数为0.6的感性负载供电后，负载电流的有效值为（　）。",
      "A":"$\\frac{20\\times10^3}{220}=90.9A$","B":"$\\frac{8\\times10^3}{0.6\\times220}=60.6A$","C":"$\\frac{8\\times10^3}{220}=36.36A$","D":"$\\frac{20\\times10^3}{0.6\\times220}=151.5A$"},
 695:{"question":"图（A）所示时序逻辑电路的工作波形如图（B）所示，由此可知，图（A）电路是一个（　）。"},
 840:{"A":"$\\lim\\limits_{x\\to0}e^{\\frac1x}$存在",
     "B":"$\\lim\\limits_{x\\to0^-}e^{\\frac1x}$存在",
     "C":"$\\lim\\limits_{x\\to0^+}e^{\\frac1x}$存在",
     "D":"$\\lim\\limits_{x\\to0^+}e^{\\frac1x}$存在，$\\lim\\limits_{x\\to0^-}e^{\\frac1x}$不存在，从而$\\lim\\limits_{x\\to0}e^{\\frac1x}$不存在"},
 1626:{"A":"A","B":"B","C":"C","D":"D"},
}
for i,fields in FIX.items():
    q=byid.get(i)
    assert q, f"missing {i}"
    q.update(fields)
out=json.dumps(Q,ensure_ascii=False,indent=2)
open(P,'w',encoding='utf-8',newline='').write(out)
print("size",os.path.getsize(P))
