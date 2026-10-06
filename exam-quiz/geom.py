# -*- coding: utf-8 -*-
import sys, os, re, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\题目和答案pdf"
pub=pymupdf.open(os.path.join(D,"公共基础分类版真题详解（13~24）_题目.pdf"))
# locate target question stems and report page
STEMS={
 306:"简支梁AB 的剪力图和弯矩图如图示",
 448:"则数字信号F = A + B",
 546:"图示圆轴固定端最上缘A点单元体",
 568:"则数字信号F",
 666:"梁的正确挠曲线是图示四条曲线中的",
 669:"其中具有最大临界载荷",
 784:"发生最大弯曲正应力的截面是",
 904:"图示梁的正确挠曲线大致形状",
 908:"图示四根细长压杆的抗弯刚度EI相同",
 1262:"其中图形关于坐标轴X、y 的静矩",
 1292:"该电路的小信号模型为",
 932:"输出电压波形为",
}
OUT=open(r"C:\Users\Administrator\.qclaw\workspace\geom.txt","w",encoding="utf-8")
for qid,stem in STEMS.items():
    for i in range(len(pub)):
        t=pub[i].get_text()
        if stem in t:
            OUT.write(f"\n######## id{qid} p{i+1}  (stem found)\n")
            gi=pub[i].get_images(full=True)
            OUT.write(f"  images: {[(g[0], g[2], g[3]) for g in gi]}\n")
            for g in gi:
                for r in pub[i].get_image_rects(g[0]):
                    OUT.write(f"    IMG xref{g[0]} rect=({r.x0:.0f},{r.y0:.0f},{r.x1:.0f},{r.y1:.0f})\n")
            break
OUT.close(); print(open(r"C:\Users\Administrator\.qclaw\workspace\geom.txt",encoding='utf-8').read())
