import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

# 读取试题册
with open(r'D:\应用程序开发\刷题\prof2_questions_raw.txt', 'r', encoding='utf-8') as f:
    q_raw = f.read()

# 读取解析册
with open(r'D:\应用程序开发\刷题\prof2_answers_raw.txt', 'r', encoding='utf-8') as f:
    a_raw = f.read()

# 广告过滤
ad_keywords = ['微信公众号', '基础学习交流', 'QQ 群', 'QQ群', '微信扫码', '注册勘察设计']
def is_ad(line):
    if '小注教育答案' in line:
        return False
    if '小注教育' in line and '答案' not in line:
        return True
    return any(kw in line for kw in ad_keywords)

# 解析试题册
# 年份标题模式
year_title_pattern = re.compile(r'(\d{4})\s*年(?:（补考）)?\s*注册岩土专业基础真题\s*$')
year_title_with_bu_pattern = re.compile(r'(\d{4})\s*年（补考）\s*注册岩土专业基础真题\s*$')
# 题号模式："1、" 开头
qnum_pattern = re.compile(r'^(\d{1,2})[、.．]\s*(.*)$')
# 选项模式
opt_pattern = re.compile(r'^[（(]\s*([A-D])\s*[）)]\s*(.*)$')

def parse_book(raw_text):
    """解析试题册或解析册，返回按年份组织的题目"""
    lines = raw_text.split('\n')
    result = {}  # {year: {qnum: {question, A, B, C, D}}}
    current_year = None
    current_qnum = None
    current_opt = None
    current_question = ''
    current_options = {'A': '', 'B': '', 'C': '', 'D': ''}

    for line in lines:
        line = line.strip()
        if not line or is_ad(line):
            continue

        # 匹配年份标题（区分补考）
        ym = re.search(r'(\d{4})\s*年（补考）\s*注册岩土专业基础真题', line)
        if ym:
            year_key = ym.group(1) + '补'
        else:
            ym = re.search(r'(\d{4})\s*年\s*注册岩土专业基础真题', line)
            if ym:
                year_key = ym.group(1)
            else:
                year_key = None

        if year_key:
            # 保存上一题
            if current_year and current_qnum:
                if current_year not in result:
                    result[current_year] = {}
                result[current_year][current_qnum] = {
                    'question': current_question.strip(),
                    'A': current_options['A'],
                    'B': current_options['B'],
                    'C': current_options['C'],
                    'D': current_options['D']
                }
            current_year = year_key
            current_qnum = None
            current_question = ''
            current_options = {'A': '', 'B': '', 'C': '', 'D': ''}
            continue

        if not current_year:
            continue

        # 匹配题号
        qm = qnum_pattern.match(line)
        if qm:
            # 保存上一题
            if current_qnum:
                if current_year not in result:
                    result[current_year] = {}
                result[current_year][current_qnum] = {
                    'question': current_question.strip(),
                    'A': current_options['A'],
                    'B': current_options['B'],
                    'C': current_options['C'],
                    'D': current_options['D']
                }
            current_qnum = int(qm.group(1))
            current_question = qm.group(2)
            current_options = {'A': '', 'B': '', 'C': '', 'D': ''}
            current_opt = None
            continue

        if not current_qnum:
            continue

        # 匹配选项
        om = opt_pattern.match(line)
        if om:
            current_opt = om.group(1)
            current_options[current_opt] = om.group(2).strip()
        elif current_opt:
            # 续接选项
            if current_options[current_opt]:
                current_options[current_opt] += line
            else:
                current_question += line
        else:
            # 题干续行
            current_question += line

    # 保存最后一题
    if current_year and current_qnum:
        if current_year not in result:
            result[current_year] = {}
        result[current_year][current_qnum] = {
            'question': current_question.strip(),
            'A': current_options['A'],
            'B': current_options['B'],
            'C': current_options['C'],
            'D': current_options['D']
        }

    return result

questions = parse_book(q_raw)
print("试题册解析结果:")
for year in sorted(questions.keys()):
    print(f"  {year}年: {len(questions[year])}道题")

# 解析解析册
answer_pattern = re.compile(r'^(\d{1,2})[、.．]\s*小注教育答案\s*[：:]\s*【([A-D])】')
analysis_start = re.compile(r'^解题分析\s*[：:]\s*(.*)$')

def parse_answers(raw_text):
    lines = raw_text.split('\n')
    result = {}  # {year: {qnum: {answer, analysis}}}
    current_year = None
    current_qnum = None
    current_answer = ''
    current_analysis = ''
    in_analysis = False

    for line in lines:
        line = line.strip()
        if not line or is_ad(line):
            continue

        # 匹配年份标题（区分补考）
        ym = re.search(r'(\d{4})\s*年（补考）\s*注册岩土专业基础真题解析', line)
        if ym:
            year_key = ym.group(1) + '补'
        else:
            ym = re.search(r'(\d{4})\s*年\s*注册岩土专业基础真题解析', line)
            if ym:
                year_key = ym.group(1)
            else:
                year_key = None

        if year_key:
            if current_year and current_qnum:
                if current_year not in result:
                    result[current_year] = {}
                result[current_year][current_qnum] = {
                    'answer': current_answer,
                    'analysis': current_analysis.strip()
                }
            current_year = year_key
            current_qnum = None
            current_analysis = ''
            in_analysis = False
            continue

        if not current_year:
            continue

        # 匹配答案
        am = answer_pattern.match(line)
        if am:
            if current_qnum:
                if current_year not in result:
                    result[current_year] = {}
                result[current_year][current_qnum] = {
                    'answer': current_answer,
                    'analysis': current_analysis.strip()
                }
            current_qnum = int(am.group(1))
            current_answer = am.group(2)
            current_analysis = ''
            in_analysis = False
            continue

        if not current_qnum:
            continue

        # 匹配解析开始
        aysm = analysis_start.match(line)
        if aysm:
            in_analysis = True
            current_analysis = aysm.group(1)
        elif in_analysis:
            current_analysis += line

    # 保存最后一题
    if current_year and current_qnum:
        if current_year not in result:
            result[current_year] = {}
        result[current_year][current_qnum] = {
            'answer': current_answer,
            'analysis': current_analysis.strip()
        }

    return result

answers = parse_answers(a_raw)
print("\n解析册解析结果:")
for year in sorted(answers.keys()):
    print(f"  {year}年: {len(answers[year])}道题")

# 合并题目和答案
merged = {}
for year in questions:
    merged[year] = {}
    for qnum in questions[year]:
        q = questions[year][qnum]
        a = answers.get(year, {}).get(qnum, {'answer': '', 'analysis': ''})
        merged[year][qnum] = {
            'question': q['question'],
            'A': q['A'],
            'B': q['B'],
            'C': q['C'],
            'D': q['D'],
            'answer': a['answer'],
            'analysis': a['analysis']
        }

print("\n合并结果:")
for year in sorted(merged.keys()):
    print(f"  {year}年: {len(merged[year])}道题")

# 保存
with open(r'D:\应用程序开发\刷题\prof2_merged.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)
print("\n已保存 prof2_merged.json")
