# -*- coding: utf-8 -*-
import sys, os
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
D=r"C:\Users\Administrator\.qclaw\workspace\chk"
def load(n): return Image.open(os.path.join(D,n)).convert("RGB")
groups=[
 ("g306",["id771_2016_67_3.png","id771_2016_67_4.png","id771_2016_67_5.png"]),
 ("g448",["id1099_2017_89_3.png"]),
 ("g546",["id821_2018_67_4.jpeg"]),
 ("g568",["id1102_2018_89_2.jpeg"]),
 ("g666",["id782_2019_67_crop.png"]),
 ("g784",["id784_2020_65_crop.png"]),
 ("g904",["id787_2021_65_crop.png"]),
 ("g908",["id825_2021_69_crop.png"]),
 ("g928",["id1110_2021_89_2.png"]),
]
for name,items in groups:
    ims=[load(i) for i in items]
    W=max(i.width for i in ims)+20
    H=sum(i.height+20 for i in ims)+10
    cv=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(cv); y=5
    for it,im in zip(items,ims):
        d.text((5,y),it,fill="red"); y+=16
        cv.paste(im,(10,y)); y+=im.height+6
    cv.save(os.path.join(D,f"_{name}.png"))
    print(name,"ok")
