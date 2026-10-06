# -*- coding: utf-8 -*-
"""把 48 道题干/选项侧 T1 题目的公式按原卷图片重写，写回 questions.json"""
import os, json, shutil, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
BAK = os.path.join(ROOT, '_fix_backup', 'questions_BEFORE_T1FIX.json')

IMG = '{IMGS}'

F = {}


def setf(tid, **kw):
    F.setdefault(tid, {}).update(kw)


setf(8,
     A=r'$\int_0^{+\infty} e^{-x} dx$',
     B=r'$\int_0^{+\infty} \frac{1}{1+x^2} dx$',
     C=r'$\int_0^{+\infty} \frac{\ln x}{x} dx$',
     D=r'$\int_0^{1} \frac{1}{\sqrt{1-x^2}} dx$')

setf(12, question=r'正项级数$\sum_{n=1}^{\infty}a_n$的部分和数列$\{s_n\}$($s_n=\sum_{k=1}^{n}a_k$)有上界是该级数收敛的:( ).')

setf(17,
     A=r'$\sum_{n=0}^{\infty} 3x^n$',
     B=r'$\sum_{n=0}^{\infty} 3^n x^n$',
     C=r'$\sum_{n=0}^{\infty} \frac{1}{3^{\frac{n}{2}}} x^n$',
     D=r'$\sum_{n=0}^{\infty} \frac{1}{3^{n+1}} x^n$')

setf(61,
     A=r'$\tau_{max}=\frac{4F}{\pi d^2}$',
     B=r'$\tau_{max}=\frac{8F}{\pi d^2}$',
     C=r'$\tau_{max}=\frac{12F}{\pi d^2}$',
     D=r'$\tau_{max}=\frac{2F}{\pi d^2}$')

setf(131, question=r'级数$\sum_{n=1}^{\infty}(-1)^n\frac{1}{n^{p-1}}$:( ).')

setf(136, question=r'级数$\sum_{n=1}^{\infty}\frac{(2x+1)^n}{n}$的收敛域是:( ).',
     A=r'$(-1,1)$', B=r'$[-1,1]$', C=r'$[-1,0)$', D=r'$(-1,0)$')

setf(167,
     question=r'图示边长为 a 的正方形物块 OABC,已知:$F_1=F_2=F_3=F_4=F$,力偶矩$M_1=M_2=Fa$,该力系向O点简化后的主矢及主矩应力:( ).' + IMG,
     A=r'$F_R=0N,M_0=4Fa$(顺时针)',
     B=r'$F_R=0N,M_0=3Fa$(逆时针)',
     C=r'$F_R=0N,M_0=2Fa$(逆时针)',
     D=r'$F_R=0N,M_0=2Fa$(顺时针)')

setf(207,
     question=r'图示非周期信号$u(t)$如图所示,若利用单位阶跃函数$\varepsilon(t)$将其写成时间函数表达式,则$u(t)$等于:( ).' + IMG,
     A=r'$5-1=4V$',
     B=r'$5\varepsilon(t)+\varepsilon(t-t_0)V$',
     C=r'$5\varepsilon(t)-4\varepsilon(t-t_0)V$',
     D=r'$5\varepsilon(t)-4\varepsilon(t+t_0)V$')

setf(253,
     A=r'$\sum_{n=1}^{\infty}(-1)^{n-1}\frac{1}{n}$',
     B=r'$\sum_{n=1}^{\infty}(-1)^{n-1}\frac{1}{\sqrt{n}}$',
     C=r'$\sum_{n=1}^{\infty}\frac{n^2}{1+n^2}$',
     D=r'$\sum_{n=1}^{\infty}\frac{\sin\frac{3}{2}n}{n^2}$')

setf(256, question=r'幂级数$\sum_{n=0}^{\infty}\frac{(-1)^n}{2^n}x^n$在$|x|<2$的和函数是:( ).')

setf(267,
     question=r'在卡诺循环过程中,理想气体在一个绝热过程中所做的功为$W_1$,内能变化为$\Delta E_1$,则在另一绝热中气体做功$W_2$,内能变化为$\Delta E_2$,则$W_1$,$W_2$,$\Delta E_1$,$\Delta E_2$间关系为:( ).',
     A=r'$W_2=W_1,\Delta E_2=\Delta E_1$',
     B=r'$W_2=-W_1,\Delta E_2=\Delta E_1$',
     C=r'$W_2=-W_1,\Delta E_2=-\Delta E_1$',
     D=r'$W_2=W_1,\Delta E_2=-\Delta E_1$')

setf(318,
     question=r'真空中,点电荷$q_1$和$q_2$的空间位置如图所示,若$q_1$为正电荷,且$q_2=-q_1$,则A点的电场强度的方向是:( ).' + IMG,
     A=r'从A点指向$q_1$',
     B=r'从A点指向$q_2$',
     C=r'垂直于$q_1q_2$连线,方向向上',
     D=r'垂直于$q_1q_2$连线,方向向下')

setf(326, question=r'图示电压信号$u_o$是:( ).' + IMG)

setf(371,
     question=r'设$L$是椭圆$\begin{cases}x=a\cos\theta\\y=b\sin\theta\end{cases}$$(a>0,b>0)$的上半椭圆周,取顺时针方向,则曲线积分$\int_L y^2dx$等于:( ).',
     A=r'$\frac{5}{3}ab^2$', B=r'$\frac{4}{3}ab^2$', C=r'$\frac{2}{3}ab^2$', D=r'$\frac{1}{3}ab^2$')

setf(376, question=r'幂级数$\sum_{n=1}^{\infty}\frac{x^n}{n!}$的和函数$s(x)$等于:( ).',
     A=r'$e^x$', B=r'$e^x+1$', C=r'$e^x-1$', D=r'$\cos x$')

setf(380,
     question=r'设$\lambda_1=6,\lambda_2=\lambda_3=3$为 3 阶实对称矩阵A的特征值,属于$\lambda_2=\lambda_3=3$的特征向量为$\xi_2=(-1,0,1)^T,\xi_3=(1,2,1)^T$,则属于特征值$\lambda_1=6$的特征向量是:( ).',
     A=r'$(1,-1,1)^T$', B=r'$(1,1,1)^T$', C=r'$(0,2,2)^T$', D=r'$(2,2,0)^T$')

setf(383,
     question=r'设$\hat{\theta}$是参数$\theta$的一个无偏估计量,又方差$D(\hat{\theta})>0$,则下面结论中正确的是:( ).',
     A=r'$(\hat{\theta})^2$是$\theta^2$的无偏估计量',
     B=r'$(\hat{\theta})^2$不是$\theta^2$的无偏估计量',
     C=r'不能确定$(\hat{\theta})^2$是还是不是$\theta^2$的无偏估计量',
     D=r'$(\hat{\theta})^2$不是$\theta^2$的估计量')

setf(413,
     question=r'图示均质圆轮,质量m,半径R.由挂在绳上的重为W的物块使其绕O运动.设重物速度为v,不计绳重,则系统动量,动能大小是( ).' + IMG,
     A=r'$\frac{W}{g}\cdot v;\frac{1}{2}\frac{R^2W^2}{g}\left(\frac{1}{2}mg+w\right)$',
     B=r'$mv;\frac{1}{2}\frac{R^2W^2}{g}\left(\frac{1}{2}mg+w\right)$',
     C=r'$\frac{W}{g}\cdot v+mv;\frac{1}{2}\frac{R^2W^2}{g}\left(\frac{1}{2}mg-w\right)$',
     D=r'$\frac{W}{g}\cdot v-mv;\frac{W}{g}\cdot v+mv$')

setf(492,
     A=r'$\sum_{n=1}^{\infty}\frac{1}{n(n+1)}$',
     B=r'$\sum_{n=1}^{\infty}\frac{1}{n^{\frac{3}{2}}}$',
     C=r'$\sum_{n=1}^{\infty}\left(\frac{n}{2n+1}\right)^2$',
     D=r'$\sum_{n=1}^{\infty}(-1)^n\frac{1}{\sqrt{n}}$')

setf(501,
     question=r'设随机变量X的分布函数为$F(x)=\begin{cases}x^3, & 0<x\leq1\\1, & x>1\end{cases}$,则数学期望:( ).',
     A=r'$\int_0^1 3x^2 dx$',
     B=r'$\int_0^1 3x^3 dx$',
     C=r'$\int_0^1 \frac{x^4}{4} dx+\int_1^{+\infty} x dx$',
     D=r'$\int_0^{+\infty} 3x^3 dx$')

setf(521,
     question=r'下列各反应等于$CO_2$的标准摩尔生成焓$\Delta_f H_m^\ominus$的是( ).',
     A=r'$C(金刚石)+O_2(g)\rightarrow CO_2(g)$',
     B=r'$CO(g)+1/2O_2(g)\rightarrow CO_2(g)$',
     C=r'$C(石墨)+O_2(g)\rightarrow CO_2(g)$',
     D=r'$2C(石墨)+2O_2(g)\rightarrow 2CO_2(g)$')

setf(615, question=r'关于级数$\sum_{n=1}^{\infty}(-1)^n\frac{1}{n^p}$收敛性的正确结论是:( ).')

setf(617, question=r'幂级数$\sum_{n=1}^{\infty}(-1)^{n-1}\frac{x^{2n-1}}{2n-1}$的收敛域是:( ).',
     A=r'$[-1,1]$', B=r'$(-1,1]$', C=r'$[-1,1)$', D=r'$(-1,1)$')

setf(623,
     question=r'设总体X服从均匀分布$U(1,\theta)$,$\bar{X}=\frac{1}{n}\sum_{i=1}^{n}X_i$,则$\theta$的矩估计为:( ).',
     A=r'$\bar{X}$', B=r'$2\bar{X}$', C=r'$2\bar{X}-1$', D=r'$2\bar{X}+1$')

setf(684,
     question=r'设图示变压器为理想器件,且$u_s=90\sqrt{2}\sin(\omega t)V$,开关S闭合时,信号源的内阻$R_1$与信号源右侧电路的等效电阻相等,那么,开关s断开后,电压:( ).' + IMG,
     A=r'$u_1$,因变压器的匝数比K、电阻$R_L$、$R_1$未知而无法确定',
     B=r'$u_1=45\sqrt{2}\sin\omega t V$',
     C=r'$u_1=60\sqrt{2}\sin\omega t V$',
     D=r'$u_1=30\sqrt{2}\sin\omega t$')

setf(731,
     question=r'设D是由直线$y=x$和圆$x^2+(y-1)^2=1$所围成且在直线$y=x$下方的平面区域,则二重积分$\iint_D xdxdy$的值等于:( ).',
     A=r'$\int_0^{\frac{\pi}{2}}\cos\theta d\theta\int_0^{2\cos\theta}\rho^2 d\rho$',
     B=r'$\int_0^{\frac{\pi}{2}}\sin\theta d\theta\int_0^{2\sin\theta}\rho^2 d\rho$',
     C=r'$\int_0^{\frac{\pi}{4}}\sin\theta d\theta\int_0^{2\sin\theta}\rho^2 d\rho$',
     D=r'$\int_0^{\frac{\pi}{4}}\cos\theta d\theta\int_0^{2\sin\theta}\rho^2 d\rho$')

setf(735,
     A=r'$\sum_{n=1}^{\infty}\frac{n^2}{3n^4+1}$',
     B=r'$\sum_{n=2}^{\infty}\frac{1}{\sqrt[3]{n(n-1)}}$',
     C=r'$\sum_{n=1}^{\infty}\frac{(-1)^n}{\sqrt{n}}$',
     D=r'$\sum_{n=1}^{\infty}\frac{5}{3^n}$')

setf(737,
     question=r'若幂级数$\sum_{n=1}^{\infty}a_n(x+2)^n$在$x=0$处收敛,在$x=-4$处发散,则幂级数$\sum_{n=1}^{\infty}a_n(x-1)^n$的收敛域是:( ).',
     A=r'$(-1,3)$', B=r'$[-1,3)$', C=r'$(-1,3]$', D=r'$[-1,3]$')

setf(855,
     A=r'$\sum_{n=1}^{\infty}\frac{8^n}{7^n}$',
     B=r'$\sum_{n=1}^{\infty}n\sin\frac{1}{n}$',
     C=r'$\sum_{n=1}^{\infty}\frac{1}{\sqrt{n}}$',
     D=r'$\sum_{n=1}^{\infty}(-1)^{n-1}\frac{1}{n}$')

setf(856, question=r'级数$\sum_{n=1}^{\infty}n\left(\frac{1}{2}\right)^{n-1}$的和是:( )')

setf(863,
     question=r'设$X_1,X_2,...,X_n$是来自总体$X\sim N(\mu,\sigma^2)$的样本,$\bar{X}$是$X_1,X_2,...,X_n$的样本均值,则$\sum_{i=1}^{n}\frac{(X_i-\bar{X})^2}{\sigma^2}$服从的分布是:( )',
     A=r'$F(n)$', B=r'$t(n)$', C=r'$\chi^2(n)$', D=r'$\chi^2(n-1)$')

setf(971,
     question=r'设D是圆域:$x^2+y^2\leq1$,则二重积分$\iint_D xdxdy$等于:( ).',
     A=r'$2\int_0^{\pi}d\theta\int_0^1 r^2\sin\theta dr$',
     B=r'$\int_0^{2\pi}d\theta\int_0^1 r^2\cos\theta dr$',
     C=r'$4\int_0^{\frac{\pi}{2}}d\theta\int_0^1 r\cos\theta dr$',
     D=r'$4\int_0^{\frac{\pi}{4}}d\theta\int_0^1 r^3\cos\theta dr$')

setf(973,
     A=r'$\sum_{n=2}^{\infty}(-1)^n\frac{1}{\ln n}$',
     B=r'$\sum_{n=1}^{\infty}(-1)^n\frac{1}{n^{\frac{3}{2}}}$',
     C=r'$\sum_{n=1}^{\infty}(-1)^n\frac{n}{n+2}$',
     D=r'$\sum_{n=1}^{\infty}\frac{\sin\left(\frac{4n\pi}{3}\right)}{n^3}$')

setf(976,
     question=r'若幂级数$\sum_{n=1}^{\infty}a_nx^n$的收敛半径为$3$,则幂级数$\sum_{n=1}^{\infty}na_n(x-1)^{n+1}$的收敛区间是:( ).')

setf(1020,
     question=r'如图所示,钢板用销轴连接在铰支座上,下端受轴向拉力 F,已知钢板和销轴的许用挤压应力均为$[\sigma_{bs}]$,则销轴的合理直径d是( )' + IMG,
     A=r'$d\geq\frac{F}{t[\sigma_{bs}]}$',
     B=r'$d\geq\frac{F}{2t[\sigma_{bs}]}$',
     C=r'$d\geq\frac{F}{b[\sigma_{bs}]}$',
     D=r'$d\geq\frac{F}{2b[\sigma_{bs}]}$')

setf(1095, question=r'已知级数$\sum_{n=1}^{\infty}a_n$收敛,$\{S_n\}$是它的前$n$项部分和数列,则$\{S_n\}$必是:( ).')

setf(1103,
     question=r'设$X,Y$为两个随机变量,$E(X)=1,E(Y)=2,D(X)=1,D(Y)=4$,X与Y的相关系数$\rho_{xy}=0.6$,则数学期望$E[(2X-Y+1)^2]$的值等于:( ).')

setf(1122,
     question=r'已知$E^{\theta}\left(\frac{Cu^{2+}}{Cu}\right)=0.34V$,现测得$E\left(\frac{Cu^{2+}}{Cu}\right)=0.30V$,说明该电极中$C(Cu^{2+})$为( )',
     A=r'$C(Cu^{2+})>1.0$ mol/L',
     B=r'$C(Cu^{2+})<1$ mol/L',
     C=r'$C(Cu^{2+})=1$ mol/L',
     D=r'不确定')

setf(1140,
     question=r'钢板用铆钉固定再铰支座上,下端受轴向拉力 F,已知铰链轴的需用切应力为$[\tau]$,则铰链轴的合理直径d为:( )',
     A=r'$d^2\geq\frac{4F}{\pi[\tau]}$',
     B=r'$d^2\geq\frac{2F}{\pi[\tau]}$',
     C=r'$d^2\geq\frac{F}{\pi[\tau]}$',
     D=r'$d^2\geq\frac{F}{2\pi[\tau]}$')

setf(1214,
     question=r'设有级数$\sum_{n=1}^{\infty}\frac{1}{1+a^n}$$(a>0)$,在下面结论中,错误的是:( ).',
     A=r'$a>1$时级数收敛',
     B=r'$a\leq1$时级数收敛',
     C=r'$a<1$时级数发散',
     D=r'$a=1$时级数发散')

setf(1217,
     question=r'幂级数$\sum_{n=1}^{\infty}(2n-1)x^{n-1}$在$|x|<1$内的和函数是:( ).',
     A=r'$\frac{1}{(1-x)^2}$',
     B=r'$\frac{1+x}{(1-x)^2}$',
     C=r'$\frac{x}{(1-x)^2}$',
     D=r'$\frac{1-x}{(1+x)^2}$')

setf(1280,
     question=r'在图示电路中,$u(t)=10\sin1000tV$时,$I_L=0.1A$,$I_C=0.1A$,当激励改为$u(t)=10\sin2000tV$后:( ).' + IMG,
     A=r'$I_L<0.1A$,$I_C>0.1A$,$I\neq I_R$',
     B=r'$I_L>0.1A$,$I_C<0.1A$,$I_1=0$',
     C=r'$I_L<0.1A$,$I_C>0.1A$,$I_1=I_R$',
     D=r'$I_L>0.1A$,$I_C<0.1A$,$I_1=I_R$')

setf(1294,
     question=r'图(a)所示电路中,复位信号、数据输入及时钟脉冲信号如图(b)所示,经分析可知,在第一个和第二个时钟脉冲的下降沿过后,输出Q先后等于:( ).' + IMG +
              r'附:JK触发器的逻辑状态表为:$\begin{array}{|c|c|c|}\hline J&K&Q_{n+1}\\\hline0&0&Q_n\\\hline0&1&0\\\hline1&0&1\\\hline1&1&\overline{Q_n}\\\hline\end{array}$')

setf(1336,
     question=r'幂级数$\sum_{n=1}^{\infty}(-1)^{n-1}\frac{(x+1)^n}{n}$的收敛域为:( ).',
     A=r'$[-2,0]$', B=r'$[-2,0)$', C=r'$(-2,0]$', D=r'$(-2,0)$')

setf(1372,
     question=r'四连杆机构如图所示.已知曲柄$O_1A$长为r,AM长为l,角速度为$\omega$、角加速度为$\varepsilon$,则固连在AB杆上的物块M的速度和切向加速度的大小为:( ).' + IMG,
     A=r'$v_M=l\omega$,$a_M^{\tau}=l\varepsilon$',
     B=r'$v_M=l\omega$,$a_M^{\tau}=r\varepsilon$',
     C=r'$v_M=r\omega$,$a_M^{\tau}=r\varepsilon$',
     D=r'$v_M=r\omega$,$a_M^{\tau}=l\varepsilon$')

setf(1375,
     question=r'均质圆柱体半径为R,质量为m,绕关于对纸面垂直的固定水平轴自由转动,如图所示.当圆柱体转动到$\theta=90^{\circ}$位置时,其角加速度是:( ).' + IMG,
     A=r'$\frac{g}{3R}$', B=r'$\frac{g}{2R}$', C=r'$\frac{4g}{3R}$', D=r'$\frac{2g}{3R}$')

setf(1380,
     question=r'图示简支梁两端由铰链约束,已知铰链轴的许用切应力为$[\tau]$,梁中间受集中力F作用,则铰链轴的合理直径d是:( ).' + IMG,
     A=r'$d^2\geq\frac{4F}{\pi[\tau]}$',
     B=r'$d^2\geq\frac{2F}{\pi[\tau]}$',
     C=r'$d^2\geq\frac{F}{\pi[\tau]}$',
     D=r'$d^2\geq\frac{F}{2\pi[\tau]}$')

setf(1410,
     question=r'根据$u_1$和$u_2$的波形可知,图信号处理器是:( ).',
     A=r'截止频率小于$\frac{1}{T}$的高通滤波器',
     B=r'截止频率大于$\frac{1}{T}$的高通滤波器',
     C=r'截止频率小于$\frac{1}{T}$的低通滤波器',
     D=r'截止频率小于$\frac{1}{T}$的低通滤波器')


def main():
    data = json.load(open(DB, encoding='utf-8'))
    byid = {q['id']: q for q in data}
    if not os.path.isdir(os.path.dirname(BAK)):
        os.mkdir(os.path.dirname(BAK))
    if not os.path.exists(BAK):
        shutil.copy2(DB, BAK)
    miss = [t for t in F if t not in byid]
    if miss:
        print('MISSING IDS', miss); return 1
    nchg = 0
    for tid, fields in F.items():
        q = byid[tid]
        for f, new in fields.items():
            old = str(q.get(f) or '')
            if IMG in new:
                i = old.find('<br><img')
                if i < 0:
                    print('!! id=%s %s 无图片但模板含 {IMGS}' % (tid, f)); return 1
                new = new.replace(IMG, old[i:])
            if new != old:
                q[f] = new
                nchg += 1
    txt = json.dumps(data, ensure_ascii=False, indent=2)
    with open(DB, 'w', encoding='utf-8', newline='\r\n') as fh:
        fh.write(txt)
    print('题目=%d 改写字段=%d' % (len(F), nchg))
    return 0


if __name__ == '__main__':
    sys.exit(main())
