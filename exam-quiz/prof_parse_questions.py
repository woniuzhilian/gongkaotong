import sys, re, json, os
sys.stdout.reconfigure(encoding='utf-8')

# 读取题目OCR文本
with open(r'D:\应用程序开发\刷题\prof_questions_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

# 按页码分割
pages = re.split(r'===PAGE_(\d+)===', raw_text)
# pages[0]是空，pages[1]是页码，pages[2]是内容，pages[3]是页码...

# 构建带页码的文本
page_texts = {}
for i in range(1, len(pages), 2):
    page_num = int(pages[i])
    content = pages[i+1] if i+1 < len(pages) else ''
    page_texts[page_num] = content

# 小科目映射：章节标题 -> 小科目名称
# 需要从文本中提取章节标题
chapter_pattern = re.compile(r'^第[一二三四五六七八九十]+章\s*(.+)$', re.MULTILINE)
part_pattern = re.compile(r'^第[一二三四五六七八九十]+部分\s*(.+)$', re.MULTILINE)

# 先收集所有章节标题和它们的页码
chapters = []  # (page_num, line_num, chapter_name)
for page_num in sorted(page_texts.keys()):
    content = page_texts[page_num]
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        m = chapter_pattern.match(line)
        if m:
            chapters.append((page_num, m.group(1).strip()))
        m2 = part_pattern.match(line)
        if m2:
            chapters.append((page_num, '【部分】' + m2.group(1).strip()))

print("章节列表:")
for pg, name in chapters:
    print(f"  第{pg}页: {name}")

# 题目标记正则
q_pattern = re.compile(r'【\s*(\d{4})\s*(补)?\s*-\s*(\d+)\s*】')

# 解析每道题
questions = []
current_small_subject = ""
current_big_subject = "专业基础"

# 合并所有页面文本，保留页码信息
all_lines = []
for page_num in sorted(page_texts.keys()):
    content = page_texts[page_num]
    lines = content.split('\n')
    for line in lines:
        all_lines.append((page_num, line))

# 过滤广告行
ad_keywords = ['加豹哥', '进超', '微信扫一扫', '获取真正', '一手资料', '扫码', '关注公众号']
def is_ad(line):
    return any(kw in line for kw in ad_keywords)

# 逐行解析
i = 0
qid = 0
while i < len(all_lines):
    page_num, line = all_lines[i]
    line = line.strip()

    # 更新章节
    m = chapter_pattern.match(line)
    if m:
        current_small_subject = m.group(1).strip()
        i += 1
        continue
    m2 = part_pattern.match(line)
    if m2:
        i += 1
        continue

    # 跳过广告和空行
    if not line or is_ad(line):
        i += 1
        continue

    # 匹配题目标记
    qm = q_pattern.search(line)
    if qm:
        qid += 1
        year = qm.group(1)
        if qm.group(2):
            year += '补'
        qnum = qm.group(3)

        # 题干：从题目标记后开始，到选项前
        question_text = line[qm.end():].strip()
        options = {'A': '', 'B': '', 'C': '', 'D': ''}
        current_opt = None

        i += 1
        # 收集题干和选项，直到下一题或结束
        while i < len(all_lines):
            next_page, next_line = all_lines[i]
            next_line = next_line.strip()

            # 检查是否是下一题
            if q_pattern.search(next_line):
                break

            # 检查是否是章节标题
            if chapter_pattern.match(next_line) or part_pattern.match(next_line):
                break

            # 跳过广告和空行
            if not next_line or is_ad(next_line):
                i += 1
                continue

            # 匹配选项
            opt_match = re.match(r'^[（(]\s*([A-D])\s*[）)]\s*(.*)$', next_line)
            if opt_match:
                current_opt = opt_match.group(1)
                opt_text = opt_match.group(2).strip()
                options[current_opt] = opt_text
            elif current_opt:
                # 续接选项内容
                if options[current_opt]:
                    options[current_opt] += next_line
                else:
                    # 可能是题干续行
                    if question_text and not question_text.endswith('）') and not question_text.endswith(')'):
                        question_text += next_line
                    else:
                        options[current_opt] = next_line
            else:
                # 题干续行
                question_text += next_line

            i += 1

        # 清理题干末尾的括号
        question_text = re.sub(r'[（(]\s*[）)]\s*。?$', '', question_text).strip()
        question_text = re.sub(r'[（(]\s*[）)]\s*$', '', question_text).strip()

        questions.append({
            'id': qid,
            'bigSubject': current_big_subject,
            'smallSubject': current_small_subject,
            'year': year,
            'question': question_text,
            'A': options['A'],
            'B': options['B'],
            'C': options['C'],
            'D': options['D'],
            'answer': '',
            'analysis': '',
            '_qnum': qnum,
            '_page': page_num
        })
    else:
        i += 1

print(f"\n解析到 {len(questions)} 道题")

# 统计小科目
subjects = {}
for q in questions:
    s = q['smallSubject']
    subjects[s] = subjects.get(s, 0) + 1
print("\n小科目统计:")
for s, c in sorted(subjects.items(), key=lambda x: -x[1]):
    print(f"  {s}: {c}道")

# 检查选项完整性
missing_opts = sum(1 for q in questions if not all([q['A'], q['B'], q['C'], q['D']]))
print(f"\n选项不完整的题目: {missing_opts}道")

# 保存中间结果
with open(r'D:\应用程序开发\刷题\prof_questions_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print("已保存 prof_questions_parsed.json")
