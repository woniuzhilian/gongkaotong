import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

# 1. 建立id到题号的映射（同之前的逻辑）
with open(r'D:\应用程序开发\刷题\questions_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.compile(r'【\s*(\d{4}\s*补?)\s*-\s*(\d+)\s*】')
matches = list(pattern.finditer(text))

# 找到重复的2016-66的位置，跳过第二个
dup_positions = []
for i, m in enumerate(matches):
    year = m.group(1).replace(' ', '')
    qnum = m.group(2)
    if year == '2016' and qnum == '66':
        dup_positions.append(i+1)
skip_pos = dup_positions[1] if len(dup_positions) > 1 else 819

id_to_qnum = {}
for qid in range(1, 1439):
    if qid < skip_pos:
        match_idx = qid - 1
    else:
        match_idx = qid
    m = matches[match_idx]
    year = m.group(1).replace(' ', '')
    qnum = m.group(2)
    id_to_qnum[qid] = f"{year}-{qnum}"

# 2. 加载JSON，筛选需配图题目
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

img_keywords = ['如图', '图所示', '图中', '下图', '上图', '图示', '见图', '图为', '图是']
img_questions = []
for q in data:
    qtext = q['question']
    if any(kw in qtext for kw in img_keywords):
        m = re.search(r'PDF第(\d+)页', qtext)
        page = m.group(1) if m else ''
        qclean = re.sub(r'【本题配图，PDF第\d+页】', '', qtext).strip()
        img_questions.append({
            'id': q['id'],
            '题号': id_to_qnum.get(q['id'], ''),
            '年份': q['year'],
            '小科目': q['smallSubject'],
            'PDF页码': page,
            '题干': qclean
        })

print(f"需配图题目共 {len(img_questions)} 道")

# 3. 生成Word文档
doc = Document()

# 设置默认字体
style = doc.styles['Normal']
font = style.font
font.name = '宋体'
font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# 标题
title = doc.add_heading('公共基础真题 - 需配图题目清单', level=1)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 说明
p = doc.add_paragraph()
p.add_run(f'共 {len(img_questions)} 道题需配图。请在每题下方空白处直接粘贴对应题目图片。').font.size = Pt(9)
p.add_run('（按小科目分组，同科目题目连续排列）').font.size = Pt(9)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph()  # 空行

# 按小科目分组
current_subject = None
for idx, q in enumerate(img_questions, start=1):
    # 科目分隔
    if q['小科目'] != current_subject:
        current_subject = q['小科目']
        doc.add_paragraph()
        h = doc.add_heading(f"【{current_subject}】", level=2)
        for run in h.runs:
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(0, 51, 102)

    # 题目信息行
    p = doc.add_paragraph()
    run = p.add_run(f"{idx}. [{q['题号']}] ")
    run.bold = True
    run.font.color.rgb = RGBColor(192, 0, 0)
    run.font.size = Pt(11)

    run2 = p.add_run(f"(id={q['id']}, PDF第{q['PDF页码']}页, {q['年份']})")
    run2.font.size = Pt(9)
    run2.font.color.rgb = RGBColor(128, 128, 128)

    # 题干
    p2 = doc.add_paragraph()
    p2.add_run(q['题干'][:200]).font.size = Pt(10)
    if len(q['题干']) > 200:
        p2.add_run('...').font.size = Pt(10)

    # 图片占位提示
    p3 = doc.add_paragraph()
    run3 = p3.add_run('  ▼ 在此处粘贴图片 ▼')
    run3.font.size = Pt(9)
    run3.font.color.rgb = RGBColor(0, 128, 0)
    run3.italic = True

    # 留出空白行供粘贴图片
    for _ in range(6):
        doc.add_paragraph()

    # 分隔线
    p4 = doc.add_paragraph()
    p4.add_run('─' * 60).font.color.rgb = RGBColor(200, 200, 200)

output_path = r'D:\应用程序开发\刷题\需配图题目清单.docx'
doc.save(output_path)
print(f"Word已保存: {output_path}")
