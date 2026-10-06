# -*- coding: utf-8 -*-
"""按原书《公共基础分类版真题详解_答案解析》重写解析字段（T1 解析侧 70 题）"""
import os, json, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
BAK = os.path.join(ROOT, '_fix_backup', 'questions_BEFORE_T1ANA.json')

F = {}
def setf(tid, **kw): F.setdefault(tid, {}).update(kw)

# ===================== 第 1 批 =====================

setf(8, analysis=r'反常积分的敛散性判定. 选项A：$\int_0^{+\infty}e^{-x}dx=-\int_0^{+\infty}e^{-x}d(-x)=-e^{-x}|_0^{+\infty}=1$；选项B，$\int_0^{+\infty}\frac{1}{1+x^2}dx=arctanx|_0^{+\infty}=\frac{\pi}{2}$；选项C，$\int_0^{+\infty}\frac{\ln x}{x}dx=\int_0^{1}\frac{\ln x}{x}dx+\int_1^{+\infty}\frac{\ln x}{x}dx=\int_0^{1}\ln x d(\ln x)+\int_1^{+\infty}\ln x d(\ln x)$ $=\frac{1}{2}(\ln x)^2|_0^1+\frac{1}{2}(\ln x)^2|_1^{+\infty}=+\infty$（注意$\lim_{x\to0^+}\frac{\ln x}{x}=\infty$，$x=0$为无穷间断点。）选项D：$\int_0^{1}\frac{1}{\sqrt{1-x^2}}dx=arcsinx|_0^1=\frac{\pi}{2}$。')

setf(40, analysis=r'同离子效应. 同离子效应：若电解质溶液中，加入含有相同离子的易容强电解质，使弱电解质解离度降低的现象。对于沉淀平衡$\mathrm{BaSO}_4\rightleftharpoons\mathrm{Ba}^{2+}+\mathrm{SO}_4^{2-}$向体系中加入$\mathrm{BaCl}_2$，使$\mathrm{Ba}^{2+}$的浓度升高，平衡向左移动，所以$\mathrm{SO}_4^{2-}$浓度随着降低。')

setf(60, analysis=r'拉伸（压缩）正应力，强度条件. 对AB杆受力对称则杆1、2的轴力分别为$F_1=F_2=\frac{F}{2}$，应力$\sigma_1=\frac{F_1}{A}$，$\sigma_2=\frac{F_2}{2A}$，可知杆1最先发生强度失效，故该结构的许用荷载应为为$[F]=2A[\sigma]$')

setf(61, analysis=r'剪切强度和挤压强度实用计算. 要求最大切应力，要先求出最大剪力。构件的受力简图如下图所示。对A点取矩，$\sum M_A=0$，得$Q_B\cdot\frac{L}{2}-F\cdot(\frac{L}{2}+L)=0$，$Q_B=3F(\uparrow)$；$\sum Y=0$，得$Q_A=3F-F=2F(\downarrow)$；综上所述，$\tau_{max}=\frac{F_{max}}{A_S}=\frac{3F}{\frac{\pi}{4}d^2}=\frac{12F}{\pi d^2}$。')

setf(131, analysis=r'$p-$级数的收敛性，以及交错级数的收敛性. Leibnitz判别法知交错级数当$p>1$时收敛，取绝对值后得到$\sum_{n=1}^{\infty}\frac{1}{n^{p-1}}$，由$p-$数的结论知当$p-1>1$即$p>2$时收敛，当$p-1\leq1$，即$p\leq2$时发散。')

setf(136, analysis=r'幂级数的收敛半径公式. 令$t=2x+1$，级数变为$\sum_{n=1}^{\infty}\frac{t^n}{n}$，收敛半径为$R=\lim_{n\to\infty}\left|\frac{a_n}{a_{n+1}}\right|=\lim_{n\to\infty}\frac{\frac{1}{n}}{\frac{1}{n+1}}=1$，当$t=1$时，级数为$\sum_{n=1}^{\infty}\frac{1}{n}$，发散，当$t=-1$时，级数为$\sum_{n=1}^{\infty}\frac{(-1)^n}{n}$，此级数条件收敛，因此级数的收敛域为$-1\leq t<1$，故原级数的收敛域为$-1\leq2x+1<1\Rightarrow-1\leq x<0$。')

setf(143, analysis=r'常见的三种抽样分布的相关结论. 记$S_1^2=\frac{1}{n-1}\sum_{i=0}^{n}(X_i-\bar{X})^2$，$S_2^2=\frac{1}{n-1}\sum_{i=0}^{n}(Y_i-\bar{Y})^2$，则$\frac{(n-1)S_1^2}{\sigma^2}\sim\chi^2(n-1)$，$\frac{(n-1)S_2^2}{\sigma^2}\sim\chi^2(n-1)$，所以$\frac{\sum_{i=1}^{n}(X_i-\bar{X})^2}{\sum_{i=1}^{n}(Y_i-\bar{Y})^2}\sim F(n-1,n-1)$。')

setf(243, analysis=r'点、叉积的计算. 用$cos\theta, sin\theta$的关系和点积，叉积定义：$\alpha\cdot\beta=|\alpha|\cdot|\beta|cos\theta=2\Rightarrow\theta=\frac{\pi}{4}$，$|\alpha\times\beta|=|\alpha|\cdot|\beta|sin\theta=2\sqrt{2}\times\frac{\sqrt{2}}{2}=2$。')

# ===================== 第 2 批 =====================

setf(254, analysis=r'二重积分的计算. 被积区域为阴影部分，由于被积函数有$x^2$，所以看成$X-$型，$\iint_D x^2ydxdy=\int_0^1x^2dx\int_0^{\sqrt{1-x^2}}ydy=\frac{1}{2}\int_0^1x^2(1-x^2)dx=\frac{1}{2}(\frac{1}{3}x^3-\frac{1}{5}x^5)|_0^1=\frac{1}{15}$。或者用极坐标替换$\begin{cases}x=rcos\theta\\y=rsin\theta\end{cases}$，$dxdy\rightarrow rdrd\theta$，$0\leq\theta\leq\frac{\pi}{2}$，$0\leq r\leq1$带入得$\iint_D x^2ydxdy=\int_0^{\frac{\pi}{2}}\int_0^1(rcos\theta)^2rsin\theta rdrd\theta=-\int_0^{\frac{\pi}{2}}cos^2\theta d(cos\theta)\int_0^1r^4dr=\left(-\frac{1}{3}cos^3\theta|_0^{\frac{\pi}{2}}\right)\times\left(\frac{1}{5}r^5|_0^1\right)=\frac{1}{15}$')

setf(256, analysis=r'幂级数的和函数. 由于$\frac{1}{1+x}=\sum_{n=0}^{\infty}(-1)^nx^n,|x|<1$，所以$\sum_{n=0}^{\infty}\frac{(-1)^n}{2^n}x^n=\sum_{n=0}^{\infty}\left(-\frac{x}{2}\right)^n=\frac{1}{1-(-\frac{x}{2})}=\frac{2}{x+2}$。')

setf(278, analysis=r'弱碱解离平衡的书写及溶液PH值的计算. $K_b^{\ominus}(\mathrm{NH}_3)=\frac{[\mathrm{NH}_4^{+}][\mathrm{OH}^{-}]}{[\mathrm{NH}_3\cdot\mathrm{H}_2\mathrm{O}]}$由氨水溶液电离平衡式$\mathrm{NH}_3\cdot\mathrm{H}_2\mathrm{O}\rightleftharpoons\mathrm{NH}_4^{+}+\mathrm{OH}^{-}$得电离平衡常数计算式：又因$[\mathrm{NH}_4^{+}]=[\mathrm{OH}^{-}]$，所以将上式变形得：$[\mathrm{OH}^{-}]=\sqrt{K_b^{\ominus}(\mathrm{NH}_3)\cdot[\mathrm{NH}_3\cdot\mathrm{H}_2\mathrm{O}]}=\sqrt{1.8\times10^{-5}\times0.10}=1.34\times10^{-3}\mathrm{mol/L}$，$\mathrm{pOH}=-\lg[\mathrm{OH}^{-}]=2.87$，$\mathrm{pH}=14-\mathrm{pOH}=11.13$。')

setf(371, analysis=r'坐标曲线的积分. 上半椭圆对应$\theta$从$\pi$到0，$\int_Ly^2dx=\int_\pi^0(bsin\theta)^2asin\theta d\theta=ab^2\int_\pi^0(1-cos^2\theta)dcos\theta=\frac{4}{3}ab^2$。')

setf(375, analysis=r'二重积分的化简与求解. 用极坐标求解较为方便，令$x=rcos\theta,y=rsin\theta$，$(0\leq r\leq1,0\leq\theta\leq2\pi)$，注意$dxdy\rightarrow rdrd\theta$，则：$\iint_D\frac{dxdy}{1+x^2+y^2}=\int_0^{2\pi}d\theta\int_0^1\frac{r}{1+r^2}dr=2\pi\times\frac{1}{2}\int_0^1\frac{d(1+r^2)}{1+r^2}=\pi ln(1+r^2)|_0^1=\pi ln2$。')

setf(376, analysis=r'常用函数的幂级数展开及求和. 因为$e^x=\sum_{n=0}^{\infty}\frac{x^n}{n!}=1+\sum_{n=1}^{\infty}\frac{x^n}{n!}$。')

setf(380, analysis=r'实对称矩阵特征向量的性质. 实对称矩阵不同特征值的特征向量必正交，这里不知道具体矩阵$A$，只能用正交性排除，也就是和$\xi_2,\xi_3$正交，选项A满足，其他都不符合。')

setf(382, analysis=r'二维随机变量密度函数的性质. 作为密度函数要求满足非负性和$\int_{-\infty}^{+\infty}\int_{-\infty}^{+\infty}f(x,y)dxdy=1\Rightarrow\int_0^{+\infty}e^{by}dy\int_0^{+\infty}e^{-2ax}dx=-\frac{1}{2ab}e^{by}|_0^{+\infty}\cdot e^{-2ax}|_0^{+\infty}=1$，显然要求$e^{+\infty\cdot b}=0\Rightarrow b<0$，同理$a>0$且$-\frac{1}{2ab}=1$。')

# ===================== 第 3 批 =====================

setf(383, analysis=r'估计量的无偏性判断. 无偏估计说明$E(\hat{\theta})=\theta$，而$D(\hat{\theta})>0\Rightarrow E((\hat{\theta})^2)-(E(\hat{\theta}))^2=E((\hat{\theta})^2)-\theta^2>0$，即：$E((\hat{\theta})^2)\neq\theta^2$，选B。因为$\hat{\theta}$是$\theta$的估计量，所以D不对。')

setf(486, analysis=r'向量的点积和模长的应用. $|\alpha+\beta|^2=(\alpha+\beta)\cdot(\alpha+\beta)=|\alpha|^2+2\alpha\cdot\beta+|\beta|^2=1+4+2|\alpha||\beta|cos\theta=5+2\times1\times2\times\frac{1}{2}=7$')

setf(496, analysis=r'函数的麦克劳林展开形式. 函数$f(x)=a^x=e^{lna^x}=e^{xlna}=\sum_{0}^{\infty}\frac{(xlna)^n}{n!}$在通项中带入$n=0,1,2$即为前3项。')

setf(501, analysis=r'分布函数与密度函数的关系，随机变量期望的计算. 将$F(x)$求导得到密度函数$f(x)=\begin{cases}3x^2, & 0<x<1\\0, & \text{其他}\end{cases}$，则$E(X)=\int_{-\infty}^{+\infty}xf(x)dx=\int_0^1 3x^3dx$。')

setf(552, analysis=r'自由出流与淹没出流的流量、流速计算. 孔口出流流量：$Q=\mu A\sqrt{2gH}$；$\mu$为流量系数，同一系统下相等。')

setf(613, analysis=r'坐标曲线积分的计算. 坐标曲线的积分通常转化为参数方程的形式求解，因为曲线时圆，引入参数$\theta$，令$\begin{cases}x=cos\theta\\y=sin\theta\end{cases}(0\leq\theta\leq2\pi)$，注意为逆时针，所以$\theta$时从0到$2\pi$，用公式得$\int_L\frac{ydx-xdy}{x^2+y^2}=\int_0^{2\pi}sin\theta dcos\theta-cos\theta dsin\theta=-\int_0^{2\pi}(sin^2\theta+cos^2\theta)d\theta=-2\pi$。')

setf(615, analysis=r'$p-$级数，交错级数的绝对收敛与条件收敛的判断. 先看$\sum_{n=1}^{\infty}\left|(-1)^n\frac{1}{n^p}\right|=\sum_{n=1}^{\infty}\frac{1}{n^p}$，当$p>1$时原级数绝对收敛，当$0<p\leq1$时不绝对收敛，但是用莱布尼茨法则知原交错级数收敛，即条件收敛。')

setf(623, analysis=r'矩估算方法. 若$X$服从均匀分布，根据均匀分布的期望列等式$E(X)=\bar{X}\Rightarrow\frac{1+\theta}{2}=\bar{X}\Rightarrow\hat{\theta}=2\bar{X}-1$。')

# ===================== 第 4 批 =====================

setf(625, analysis=r'麦克斯韦速率分布函数 最概然速率是系统中任何分子最有可能具有的速率，$v_p=\sqrt{\frac{2kT}{m}}=\sqrt{\frac{2RT}{M}}$，平均速率是速率分布的数学期望值：$\langle v\rangle=\int_0^{\infty}vf(v)dv=\sqrt{\frac{8kT}{\pi m}}=\sqrt{\frac{8RT}{\pi M}}$；方均根速率是速率的平方的平均值的平方根：$v_{rms}=(\int_0^{\infty}v^2f(v)dv)^{1/2}=\sqrt{\frac{3kT}{m}}=\sqrt{\frac{3RT}{M}}$，三者比较可知选C。')

setf(721, analysis=r"斜率的计算和几何意义. $\lim_{x\to x_0}f'(x)=\infty$，说明切线的斜率为$\infty$，即$tan\theta=\infty$，角度为$\frac{\pi}{2}$，说明垂直于$x$轴。")

setf(731, analysis=r'二重积分的意义和极坐标化简. 令$x=\rho cos\theta,y=\rho sin\theta$则$dxdy=\rho d\theta d\rho$，圆的方程化简为$\rho(\rho-2sin\theta)=0$，则$\rho=2sin\theta,0\leq\theta\leq\frac{\pi}{4}$，$\iint_D xdxdy=\int_0^{\frac{\pi}{4}}\int_0^{2sin\theta}\rho cos\theta\rho d\rho d\theta=\int_0^{\frac{\pi}{4}}cos\theta\int_0^{2sin\theta}\rho^2d\rho$。')

setf(735, analysis=r'常用级数，$p-$级数，交错级数的收敛发散的判断. 选项A，$\sum_{n=1}^{\infty}\frac{n^2}{3n^4+1}\sim\sum_{n=1}^{\infty}\frac{1}{3n^2}$，收敛。选项B，$\sum_{n=2}^{\infty}\frac{1}{\sqrt[3]{n(n-1)}}\sim\sum_{n=2}^{\infty}\frac{1}{n^{\frac{1}{3}}}$发散。选项C，交错级数，用莱布尼茨判别法收敛，选项D，等比级数，收敛。')

setf(737, analysis=r'幂级数收敛域的判断. $\sum_{n=1}^{\infty}a_n(x+2)^n$在$x=0$处收敛，说明级数$\sum_{n=1}^{\infty}a_n2^n$收敛；$x=-4$发散，说明$\sum_{n=1}^{\infty}a_n(-2)^n$发散，所以$\sum_{n=1}^{\infty}a_nx^n$的收敛区域为$(-2,2]$。那么$\sum_{n=1}^{\infty}a_n(x-1)^n$的收敛域满足$-2<x-1\leq2$，即$-1<x\leq3$。')

setf(779, analysis=r'轴向拉压变形量及其计算. $\Delta L=\Delta L_{AB}+\Delta L_{BC}=\frac{3Fa}{EA}+\frac{2Fa}{EA}=\frac{5Fa}{EA}$。')

setf(812, analysis=r"分压偏置式放大电路分析. 电容具有隔直通交的作用，直流通路时，并入电容$C_E$前后，三极管射极电阻$R_E$都接地，即静态工作点不变。交流通路时，并入电容$C_E$前，输入电阻$r_i=R_{B1}//R_{B2}//(r_{be}+(1+\beta)R_E)$，电压放大倍数$A_u=-\beta\frac{R_{L}'}{r_{be}+(1+\beta)R_E}$，并入电容$C_E$后，输入电阻：$r_i=R_{B1}//R_{B2}//r_{be}$，电压放大倍数$A_u=-\beta\frac{R_{L}'}{r_{be}}$，其中：$R_{L}'=R_C//R_L$，因此，并入电容后，输入电阻和放大倍数发生变化，选择C。")

setf(855, analysis=r'常用级数，$p-$级数，交错级数的收敛发散的判断. 排除法，选项A$\sum_{n=1}^{\infty}\frac{8^n}{7^n}\neq0$，发散；选项B$\sum_{n=1}^{\infty}nsin\frac{1}{n}=\sum_{n=1}^{\infty}\frac{sin\frac{1}{n}}{\frac{1}{n}}\neq0$，发散；选项C，$p-$级数$\sum_{n=1}^{\infty}\frac{1}{n^{\frac{1}{2}}}$，$\frac{1}{2}<1$，发散；只有选项D满足题意。')

# ===================== 第 5 批 =====================

setf(856, analysis=r"常用函数的幂级数展开及求和. 代入验算最快，$\sum_{n=1}^{\infty}n\left(\frac{1}{2}\right)^{n-1}=1+2\times\frac{1}{2}+3\times\frac{1}{4}+4\times\frac{1}{8}+\cdots\cdots>3$，只有D满足。")

setf(863, analysis=r"正态总体的样本均值与样本方差. 样本方差$S^2=\frac{1}{n-1}\sum(X_i-\bar{X})^2$，有结论$\frac{(n-1)S^2}{\sigma^2}\sim\chi^2(n-1)$，选D。")

setf(971, analysis=r"极坐标系下的二重积分 圆域为单位圆，$D$：$\begin{cases}0\leq\theta\leq2\pi\\0\leq r\leq1\end{cases}$，$\iint_D xdxdy=\int_0^{2\pi}d\theta\int_0^1rcos\theta rdr=\int_0^{2\pi}d\theta\int_0^1r^2cos\theta dr$，B正确。")

setf(987, analysis=r"考查卡诺循环. 卡诺循环的热机效率为$\eta=1-\frac{Q_2}{Q_1}=1-\frac{T_2}{T_1}$，则$\frac{Q_2}{Q_1}=\frac{T_2}{T_1}=\frac{1}{n}$。")

setf(993, analysis=r"考查劈尖干涉. 在劈尖干涉中，相邻两明（暗）纹之间的距离$l=\frac{\lambda}{2nsin\theta}$，在上面的平玻璃慢慢地向上平移的过程中$\theta$保持不变，所以条纹间隔不变。")

setf(1001, analysis=r"考查弱电解质对电极电势的影响. 能够解离产生$\mathrm{H}^{+}$的物质的解离常数越小，其相应电对的标准电极电势值越小。$K_W^{\theta}(\mathrm{H}_2\mathrm{O})=1.0\times10^{-14}$最小，所以其电极电势最小。")

setf(1011, analysis=r"点的圆周运动法向加速度的计算 $a_n=\frac{v^2}{\rho}$，即，$120m/s^2=\frac{80^2m^2/s^2}{\rho}$可得：$\rho=\frac{80^2}{120}m=53.3m$。")

setf(1012, analysis=r"绕定轴转动刚体上点的加速度 由题意可知，OB=50m，则有$a_x=a_\tau=\varepsilon\times OB=1\times50cm/s^2=50cm/s^2$，$a_y=-a_n=-\omega^2OB=-2^2\times50cm/s^2=-200cm/s^2$。")

# ===================== 第 6 批 =====================

setf(1014, analysis=r"弹性力的功. （若 C 为圆心）由 $AC\perp BC$ 可知 $OB=AB$，则弹簧初始变形量为$\delta_1=(10\sqrt{2}-10)cm=0.1(\sqrt{2}-1)m$，当弹簧一端位于A时弹簧变形量$\delta_2=10cm=0.1m$。由弹性力做功$W=\frac{k}{2}(\delta_1^2-\delta_2^2)=\frac{4.9\times10^3}{2}\mathrm{N/m}\times\left[\left(0.1(\sqrt{2}-1)\right)^2-0.1^2\right]\mathrm{m}^2=-20.3\mathrm{N}\cdot\mathrm{m}$")

setf(1025, analysis=r"弯曲切应力的计算. 矩形截面梁横截面上中性轴位置的切应力为最大，此处即为该截面上的胶合面，因此$\tau_{max}=1.5\frac{F}{A}=\frac{3F}{2\times2ab}=\frac{3F}{4ab}$")

setf(1028, analysis=r"主应力，最大切应力. 在应力平面内，应力圆半径为$R=\tau_{max}=\frac{\sigma_{max}-\sigma_{min}}{2}$，图A：$\sigma_{max}=30,\sigma_{min}=-30,R=30$；图B：$\sigma_{max}=40,\sigma_{min}=-40,R=40$；图C：$\sigma_{max}=120,\sigma_{min}=100,R=10$；图D：$\sigma_{max}=40,\sigma_{min}=0,R=20$。")

setf(1093, analysis=r"极坐标系下的二重积分. 圆域为单位圆，$D$：$\begin{cases}0\leq\theta\leq2\pi\\0\leq r\leq1\end{cases}$，$\iint_D(x^2+y^2)^2dxdy=\int_0^{2\pi}d\theta\int_0^1r^4\cdot rdr=2\pi\cdot\frac{1}{6}\cdot r^6|_0^1=\frac{\pi}{3}$，选B。")

setf(1095, analysis=r"常数项级数收敛的充要条件，数列收敛的必要条件. 常数项级数收敛当且仅当部分和数列收敛，即$\sum_{n=1}^{\infty}a_n$收敛$\Leftrightarrow\lim_{n\to\infty}S_n$存在。数列收敛的必要条件为：收敛数列一定有界。选A。")

setf(1102, analysis=r"二维随机变量的概率. 根据二维随机变量的概率$\iint_D f(x,y)dxdy=1$，知$1=\iint_D Ce^{-(x+y)}dxdy=C\int_0^{\infty}e^{-x}dx\int_0^{\infty}e^{-y}dy=C(-e^{-x})|_0^{\infty}\cdot(-e^{-y})|_0^{\infty}=C$，即$C=1$，选B。")

setf(1103, analysis=r"期望和方差的性质，协方差与相关系数. 根据相关系数计算公式：$\rho_{XY}=\frac{Cov(X,Y)}{\sqrt{D(X)}\sqrt{D(Y)}}=\frac{E(XY)-E(X)E(Y)}{\sqrt{D(X)}\sqrt{D(Y)}}=\frac{E(XY)-1\times2}{\sqrt{1}\sqrt{4}}=0.6,E(XY)=3.2$，$E[(2X-Y+1)^2]=E[4X^2+Y^2-4XY+4X-2Y+1]=4E[X^2]+E[Y^2]-4E[XY]+4E[X]-2E[Y]+1=4[D(X)+E^2(X)]+[D(Y)+E^2(Y)]-4\times3.2+4\times1-2\times2+1=4[1+1]+[4+4]-11.8=4.2$，选B。")

setf(1122, analysis=r"能斯特方程与非标准电极电势计算. 根据能斯特方程，代入$E(Cu^{2+}/Cu)=E^{\ominus}(Cu^{2+}/Cu)+\frac{0.059}{2}lg[Cu^{2+}]$，可得$C(Cu^{2+})<1mol/L$。")

# ===================== 第 7 批 =====================

setf(1140, analysis=r"剪切强度. 对铰链轴做受力分析，可得剪切面上的剪切力为：$F_\tau=\frac{F}{2}$，根据剪切应力计算公式：$\tau=\frac{F_\tau}{A}=\frac{0.5F}{\frac{\pi}{4}d^2}\leq[\tau]$可得$d^2\geq\frac{2F}{\pi[\tau]}$")

setf(1147, analysis=r"切应力极值. $\tau_{max}=\frac{\sigma_1-\sigma_3}{2}$，图（A）：$\sigma_1=\sigma,\sigma_2=\sigma,\sigma_3=0,\tau_{x_1}=\frac{\sigma_1-\sigma_3}{2}=\frac{\sigma}{2}$；图（B）：$\sigma_1=\sigma,\sigma_2=0,\sigma_3=-\sigma,\tau_{m}=\frac{\sigma_1-\sigma_3}{2}=\sigma$；图(C)：$\sigma_1=2\sigma,\sigma_2=0,\sigma_2=-0.5\sigma,\tau_{\max}=\frac{\sigma_1-\sigma_3}{2}=1.25\sigma$；图（D）：$\sigma_1=2\sigma,\sigma_2=\sigma,\sigma_3=0,\tau_{x=1}=\frac{\sigma_1-\sigma_3}{2}=\sigma$。")

setf(1149, analysis=r"细长压杆临界力的计算. 细长压杆临界力$F_{cr}=\frac{\pi^2EI}{(\mu l)^2}$，图（a）为两端固定，其长度系数$\mu=0.5$，相当长度$(\mu l)_{\mathrm{a}}=0.5l$；图（b）为两段长为0.5L的一端固定、一端铰支压杆，取其中一段计算，其长度系数$\mu=0.7$，相当长度为$(\mu l)_{\mathrm{b}}=0.7\times0.5l=0.35l$，则有：$\frac{F_{crb}}{F_{cra}}=\frac{(\mu l)_{\mathrm{a}}^2}{(\mu l)_{\mathrm{b}}^2}=\frac{0.25}{0.35^2}=\frac{1}{0.7^2}$。")

setf(1214, analysis=r"正项级数的敛散性. 当$a=1$时，$\sum_{n=1}^{\infty}\frac{1}{1+a^n}=\sum_{n=1}^{\infty}\frac{1}{2}$，发散，选B。")

setf(1217, analysis=r"幂级数的和函数. $\sum_{n=1}^{\infty}(2n-1)x^{n-1}=2\sum_{n=1}^{\infty}nx^{n-1}-\sum_{n=1}^{\infty}x^{n-1}=2\sum_{n=1}^{\infty}(x^n)'-\sum_{n=1}^{\infty}x^{n-1}$ $=2(\sum_{n=1}^{\infty}x^n)'-\sum_{n=1}^{\infty}x^{n-1}=2(\frac{x}{1-x})'-\frac{1}{1-x}=2\cdot\frac{1-x+x}{(1-x)^2}-\frac{1}{1-x}=\frac{1+x}{(1-x)^2}$，选B。")

setf(1223, analysis=r"二维随机变量的概率. $1=\iint_D f(x,y)dxdy=\int_0^{+\infty}dy\int_0^{+\infty}axe^{-(x^2+y)}dx$ $=-\frac{a}{2}\int_0^{+\infty}dy\int_0^{+\infty}e^{-(x^2+y)}d[-(x^2+y)]=-\frac{a}{2}\int_0^{+\infty}e^{-(x^2+y)}|_0^{+\infty}dy=\frac{a}{2}\int_0^{+\infty}e^{-y}dy$ $=-\frac{a}{2}e^{-y}|_0^{+\infty}=\frac{a}{2}$，所以$a=2$，选C。")

# ===================== 第 8 批 =====================

setf(1329, analysis=r"空间直线的位置关系. $cos\theta=\frac{|s_1\cdot s_2|}{\sqrt{s_1}\cdot\sqrt{s_2}}=\frac{|1\times2+(-4)\cdot(-2)+1\times(-1)|}{\sqrt{1+16+1}\cdot\sqrt{4+4+1}}=\frac{9}{3\sqrt{2}\cdot3}=\frac{\sqrt{2}}{2},\theta=\frac{\pi}{4}$，选C。")

setf(1333, analysis=r"对弧长的曲线积分. 右半圆周$L$的参数方程为$\begin{cases}x=cos\theta\\y=sin\theta\end{cases},-\frac{\pi}{2}\leq\theta\leq\frac{\pi}{2}$，$\int_Lx^2ds=\int_{-\frac{\pi}{2}}^{\frac{\pi}{2}}cos^2\theta\cdot\sqrt{(-sin\theta)^2+(cos\theta)^2}d\theta=2\int_0^{\frac{\pi}{2}}\frac{1+cos2\theta}{2}d\theta=(\theta+\frac{sin2\theta}{2})|_0^{\frac{\pi}{2}}=\frac{\pi}{2}$，选C。")

setf(1336, analysis=r"幂级数的收敛域. 当$x=-2$时，$\sum_{n=1}^{\infty}(-1)^{n-1}\frac{(-1)^n}{n}=-\sum_{n=1}^{\infty}\frac{1}{n}$发散。当$x=0$时，$\sum_{n=1}^{\infty}(-1)^{n-1}\frac{1}{n}$收敛，所以收敛域为$(-2,0]$，选C。")

setf(1343, analysis=r"连续型随机变量的边缘概率密度函数. $f_X(x)=\int_{-\infty}^{+\infty}f(x,y)dy=\int_0^x4x^2dy=4x^2y|_0^x=4x^3$，选A。")

setf(1344, analysis=r"平均平动动能和平均动能公式. 平均动能$\bar{\varepsilon}=\frac{i}{2}kT$，$T$相同，自由度$i$不同；平均平动动能$\bar{w}=\frac{3}{2}kT$，$T$相同。所以，选C。")

setf(1347, analysis=r"理想气体状态方程. 根据理想气体状态方程$\frac{pV}{T}=$恒量可知，在平衡态$a$和平衡态$b$中$\frac{p_1V_1}{T_1}=\frac{p_2V_2}{T_2}$，而$\frac{p_1}{T_1}=tan\theta_1$、$\frac{p_2}{T_2}=tan\theta_2$，从图中可以看出$tan\theta_1<tan\theta_2$，所以$V_1>V_2$，故为压缩过程。")

setf(1372, analysis=r"刚体的基本运动. 因A点和M点同速度和切向加速度，所以$v_M=v_A=r\omega$，$a_M^{\tau}=a_A^{\tau}=r\varepsilon$，故选C。")

setf(1380, analysis=r"剪切强度. 由$\tau=\frac{0.5F}{2\times\frac{\pi}{4}d^2}\leq[\tau]$，解得$d^2\geq\frac{F}{\pi[\tau]}$，故选C。")

setf(1381, analysis=r"最大扭转切应力的计算. $\tau_{max1}=\frac{4T}{W_P}$，$\tau_{max2}=\frac{2T}{W_P}$，所以$\frac{\tau_{max2}}{\tau_{max1}}=\frac{1}{2}$，故选B。")

# ===================== 第 9 批（专业基础） =====================

setf(1467, analysis=r"钢材的质量等级分为A、B、C、D、E五级，由A到E表示质量由低到高。不同质量等级对冲击韧性（夏比V型缺口试验）的要求有区别。A级无冲击功要求；B级要求提供20℃时冲击功$A_k\geq34J$（纵向）；C级要求提供0℃时冲击功$A_k\geq34J$（纵向）；D级要求提供-20℃时冲击功$A_k\geq34J$（纵向）；E级要求提供-40℃时冲击功$A_k\geq27J$（纵向）。东北地区露天运行的钢结构焊接吊车梁，要考虑冲击韧性。")

setf(1524, analysis=r"混凝土局部受压强度提高系数可按下如下公式确定，$\beta_l=0.8\sqrt{\frac{A_b}{A_l}}+0.2$或者$\beta_l=\sqrt{\frac{A_b}{A_l}}$，其中$A_b\leq A_l$。")

setf(1583, analysis=r"（a）图中，令BD杆长为l，断开BD链杆，用未知力$X_1$代替，如果力法方程中的自由项$\Delta_{1t}=0$，则结构在温度作用下无内力产生，（a）图中的自由项，$\Delta_{1t}=-\frac{\sqrt{2}}{2}\alpha t\times\sqrt{2}l\times2+1\times\alpha t\times l=-\alpha tl\neq0$，故（a）图中有内力产生；同理，（b）图中，令BD杆长为l，断开BD链杆，用未知力$X_1$代替，自由项$\Delta_{1t}=-\frac{\sqrt{2}}{2}\alpha t\times\frac{\sqrt{2}}{2}l\times2+1\times\alpha t\times l=0$，（b）图中无内力产生。")

setf(1645, analysis=r"偏心受压构件实际上是弯矩M和轴心压力N共同作用的构件，在达到承载力极限状态时，截面承受的轴力N与弯矩M具有相关性。根据偏心受压构件的M-N相关曲线可以得出以下结论：①当$N\gt N_b$（$\zeta\gt\zeta_b$）时，为小偏心受压，即受压破坏，随着N的增大，截面能够承担的M将减小；②当$N=N_b$（$\zeta=\zeta_b$），达到临界破坏点，此时截面的弯矩承载力最大；③当$N\lt N_b$（$\zeta\leq\zeta_b$），为大偏心受压，当N增大时，截面能够承担的M增大。因此$N_{1u}\gt N_{2u}$时，$M_{1u}\gt M_{2u}$。")

setf(1827, analysis=r"截面受弯承载力公式：$M_u=\alpha_1f_cbh_0^2\xi_b(1-0.5\xi_b)=1\times9.6\times200\times(500-35)^2\times0.55\times(1-0.5\times0.55)=165.54\mathrm{KN}\cdot\mathrm{m}\gt155\mathrm{KN}\cdot\mathrm{m}$，抗弯满足要求。斜截面受剪要求：$V\leq0.25\beta_cf_cbh_0=0.25\times1\times9.6\times200\times(500-35)=223.2\mathrm{KN}\lt250\mathrm{KN}$，抗剪不满足要求。故选B项。")

setf(1828, analysis=r"后张法预应力混凝土轴心受拉构件，在使用阶段，加载至混凝土应力为零，由轴向拉力$N_0$产生的混凝土拉应力恰好全部抵消混凝土的有效预压应力$\sigma_{PCII}$，使截面处于消压状态，即$\sigma_{PC}=0$，这时，预应力筋的拉应力$\sigma_{p0}$是在$\sigma_{PeII}$的基础上增加$\alpha_E\sigma_{PCII}$，即：$\sigma_{p0}=\sigma_{PeII}+\alpha_E\sigma_{PCII}=\sigma_{con}-\sigma_l+\alpha_E\sigma_{PCII}$。")

setf(1844, analysis=r"根据震中距离大小，可将地震分为地方震（$\triangle\leq100$公里）、近震（$100$公里$\leq\triangle\leq1000$公里）和远震（$\triangle\gt1000$公里）。")

# ===================== 待补 =====================

def main():
    if '--dry' in sys.argv:
        bad = 0
        for tid, fields in sorted(F.items()):
            for f, new in fields.items():
                why = []
                if new.count('$') % 2: why.append('$为奇数')
                if '$$' in new: why.append('相邻$$')
                if new.endswith('\\'): why.append('结尾反斜杠')
                if why:
                    bad += 1
                    print('!! id=%s %s: %s' % (tid, f, '/'.join(why)))
        print('待改题目数=%d 字段数=%d 自检不合格=%d' % (len(F), sum(len(v) for v in F.values()), bad))
        return 0
    data = json.load(open(DB, encoding='utf-8'))
    byid = {q['id']: q for q in data}
    if not os.path.exists(BAK):
        os.makedirs(os.path.dirname(BAK), exist_ok=True)
        shutil.copy2(DB, BAK)
    nchg = 0
    for tid, fields in F.items():
        if tid not in byid:
            print('!! 库中无 id=%s' % tid); return 1
        q = byid[tid]
        for f, new in fields.items():
            old = str(q.get(f) or '')
            if new != old:
                q[f] = new; nchg += 1
    txt = json.dumps(data, ensure_ascii=False, indent=2)
    with open(DB, 'w', encoding='utf-8', newline='\r\n') as fh:
        fh.write(txt)
    print('题目=%d 改写字段=%d' % (len(F), nchg))
    return 0

if __name__ == '__main__':
    sys.exit(main())
