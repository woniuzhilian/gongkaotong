# 处理 #6 的暴露残留: id=785 / id=880 题干中的图形标注串位与裸 LaTeX,按原卷重抄
import json, os, sys, io

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

IMG785 = '<br><img src="/images/id785_2020_66_crop.png" style="max-width:100%;">'
Q785 = (u'图示梁ACB用积分法求变形时,确定积分常数的条件是(式中V为梁的挠度,$\\theta$'
        u'为梁横截面的转角,$\\Delta L$为杆DB的伸长变形:( ).') + IMG785
Q880 = (u'已知HCl(g)的$\\Delta_{\\mathrm{f}}\\mathrm{H}_{\\mathrm{m}}^{\\ominus}'
        u'=-92\\mathrm{kJ}\\cdot \\mathrm{mol}^{-1}$,则反应$\\mathrm{H}_{2}$(g)+'
        u'$\\mathrm{Cl}_{2}$(g)$\\rightarrow 2\\mathrm{HCl}$(g)的'
        u'$\\Delta_{\\mathrm{r}}\\mathrm{H}_{\\mathrm{m}}^{\\ominus}$是:( )')
NEW = {785: Q785, 880: Q880}

raw = open(DB, 'rb').read()
data = json.loads(raw.decode('utf-8'))
byid = {q['id']: q for q in data}
for tid, val in NEW.items():
    q = byid[tid]
    assert q['question'].count('$') % 2 == 0
    q['question'] = val

txt = json.dumps(data, ensure_ascii=False, indent=2)
lines = txt.count('\n') + 1
print('q=%d lines=%d dollars_even=%s' % (
    len(NEW), lines, all(v.count('$') % 2 == 0 for v in NEW.values())))
json.dump({str(k): {'question': v} for k, v in NEW.items()},
          open(os.path.join(ROOT, '_t6b_subset.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)
if '--apply' in sys.argv:
    shutil_backup = open(os.path.join(ROOT, '_fix_backup', 'questions_BEFORE_T6B.json'), 'w',
                         encoding='utf-8', newline='\r\n')
    shutil_backup.write(raw.decode('utf-8'))
    shutil_backup.close()
    with open(DB, 'w', encoding='utf-8', newline='\r\n') as fh:
        fh.write(txt)
    print('APPLIED')
