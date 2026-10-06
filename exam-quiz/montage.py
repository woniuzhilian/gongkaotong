# -*- coding: utf-8 -*-
import sys, os
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
FIN=r"C:\Users\Administrator\.qclaw\workspace\final"
for qid in [306,666,669,693,784,904,908,1040,1262]:
    ims=[Image.open(os.path.join(FIN,f'opt{qid}_{L}.png')) for L in 'ABCD']
    W=max(i.width for i in ims); H=sum(i.height for i in ims)+6*3
    cv=Image.new('RGB',(W,H),'white'); y=0
    for i in ims: cv.paste(i,(0,y)); y+=i.height+6
    cv.save(os.path.join(FIN,f'm{qid}.png'))
print('ok')
