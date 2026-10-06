import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

# 读取答案OCR文本
with open(r'D:\应用程序开发\刷题\prof_answers_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

# 按页码分割
pages = re.split(r'===PAGE_(\d+)===', raw_text)
page_texts = {}
for i in range(1, len(pages), 2):
    page_num = int(pages[i])
    content = pages[i+1] if i+1 < len(pages) else ''
    page_texts[page_num] = content

# 合并所有行
all_lines = []
for page_num in sorted(page_texts.keys()):
    content = page_texts[page_num]
    lines = content.split('\n')
    for line in lines:
        all_lines.append((page_num, line.strip()))

# 广告过滤
ad_keywords = ['加豹哥', '进超', '微信扫一扫', '获取真正', '一手资料', '扫码', '关注公众号', '注册岩土', '交流学习']
def is_ad(line):
    return any(kw in line for kw in ad_keywords)

# 题目标记正则
q_pattern = re.compile(r'【\s*(\d{4})\s*(补)?\s*-\s*(\d+)\s*】')
answer_pattern = re.compile(r'答案\s*[：:]\s*([A-D])')

# 解析答案
answers = {}  # key: "年份-题号", value: {answer, analysis}
current_key = None
current_answer = ''
current_analysis = ''
in_analysis = False

i = 0
while i < len(all_lines):
    page_num, line = all_lines[i]

    if not line or is_ad(line):
        i += 1
        continue

    # 匹配题目标记
    qm = q_pattern.search(line)
    if qm:
        # 保存上一题
        if current_key:
            answers[current_key] = {
                'answer': current_answer,
                'analysis': current_analysis.strip()
            }

        year = qm.group(1)
        if qm.group(2):
            year += '补'
        qnum = qm.group(3)
        current_key = f"{year}-{qnum}"

        # 提取答案
        am = answer_pattern.search(line)
        if am:
            current_answer = am.group(1)
        else:
            current_answer = ''

        current_analysis = ''
        in_analysis = False

        # 检查行内是否有【解题分析】
        if '解题分析' in line or '解析' in line:
            in_analysis = True
            # 提取分析内容
            idx = line.find('解题分析')
            if idx >= 0:
                current_analysis = line[idx+4:].strip()
            else:
                idx = line.find('解析')
                if idx >= 0:
                    current_analysis = line[idx+2:].strip()
    elif current_key:
        if '解题分析' in line:
            in_analysis = True
            idx = line.find('解题分析')
            current_analysis += line[idx+4:].strip()
        elif line.startswith('【') and '答案' not in line:
            # 其他标记，可能是新的部分
            pass
        else:
            if in_analysis:
                current_analysis += line
            elif answer_pattern.search(line):
                am = answer_pattern.search(line)
                if am:
                    current_answer = am.group(1)

    i += 1

# 保存最后一题
if current_key:
    answers[current_key] = {
        'answer': current_answer,
        'analysis': current_analysis.strip()
    }

print(f"解析到 {len(answers)} 道题的答案")

# 统计答案分布
ans_count = {}
for k, v in answers.items():
    a = v['answer']
    ans_count[a] = ans_count.get(a, 0) + 1
print(f"答案分布: {ans_count}")

# 保存答案
with open(r'D:\应用程序开发\刷题\prof_answers_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(answers, f, ensure_ascii=False, indent=2)

# 加载题目
with open(r'D:\应用程序开发\刷题\prof_questions_parsed.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# 合并
matched = 0
unmatched = []
for q in questions:
    key = f"{q['year']}-{q['_qnum']}"
    if key in answers:
        q['answer'] = answers[key]['answer']
        q['analysis'] = answers[key]['analysis']
        matched += 1
    else:
        unmatched.append(key)

print(f"\n题目总数: {len(questions)}")
print(f"匹配答案: {matched}")
print(f"未匹配: {len(unmatched)}")
if unmatched:
    print(f"未匹配题号: {unmatched[:20]}")

# 保存合并结果
with open(r'D:\应用程序开发\刷题\prof_all_questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print("已保存 prof_all_questions.json")
