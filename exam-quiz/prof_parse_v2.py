import sys, re, json, os
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_questions_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

pages = re.split(r'===PAGE_(\d+)===', raw_text)
page_texts = {}
for i in range(1, len(pages), 2):
    page_num = int(pages[i])
    content = pages[i+1] if i+1 < len(pages) else ''
    page_texts[page_num] = content

# 构建所有行（带页码）
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

# 章节识别：处理"第X章"单独一行，下一行是标题的情况
# 以及"第X部分"标题
chapter_num_pattern = re.compile(r'^第[一二三四五六七八九十]+章$')
part_pattern = re.compile(r'^第[一二三四五六七八九十]+部分\s*(.*)$')
chapter_full_pattern = re.compile(r'^第[一二三四五六七八九十]+章\s*(.+)$')

# 先预处理：把"第X章"和下一行的标题合并
processed_lines = []
i = 0
while i < len(all_lines):
    page_num, line = all_lines[i]

    # 检查是否是"第X章"单独一行
    if chapter_num_pattern.match(line):
        # 找下一行非空行作为标题
        j = i + 1
        while j < len(all_lines) and not all_lines[j][1].strip():
            j += 1
        if j < len(all_lines):
            title = all_lines[j][1].strip()
            # 检查下一行是否是题目标记，如果是说明标题就是空的或者下一行
            if not re.match(r'【\d{4}', title):
                merged = f"第{line[1:-1]}章 {title}"
                processed_lines.append((page_num, merged))
                i = j + 1
                continue
        processed_lines.append((page_num, line))
    else:
        processed_lines.append((page_num, line))
    i += 1

print(f"预处理后行数: {len(processed_lines)}")

# 题目标记正则
q_pattern = re.compile(r'【\s*(\d{4})\s*(补)?\s*-\s*(\d+)\s*】')

# 解析题目
questions = []
current_small_subject = ""
current_big_subject = "专业基础"
qid = 0

i = 0
while i < len(processed_lines):
    page_num, line = processed_lines[i]

    # 更新部分（大科目下的部分，但我们bigSubject固定为专业基础）
    pm = part_pattern.match(line)
    if pm:
        i += 1
        continue

    # 更新章节
    cm = chapter_full_pattern.match(line)
    if cm:
        current_small_subject = cm.group(1).strip()
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

        question_text = line[qm.end():].strip()
        options = {'A': '', 'B': '', 'C': '', 'D': ''}
        current_opt = None

        i += 1
        while i < len(processed_lines):
            next_page, next_line = processed_lines[i]

            if q_pattern.search(next_line):
                break
            if chapter_full_pattern.match(next_line) or part_pattern.match(next_line):
                break
            if not next_line or is_ad(next_line):
                i += 1
                continue

            # 匹配选项
            opt_match = re.match(r'^[（(]\s*([A-D])\s*[）)]\s*(.*)$', next_line)
            if opt_match:
                current_opt = opt_match.group(1)
                options[current_opt] = opt_match.group(2).strip()
            elif current_opt and options[current_opt]:
                # 续接选项
                options[current_opt] += next_line
            elif not current_opt:
                # 题干续行
                question_text += next_line
            else:
                options[current_opt] = next_line

            i += 1

        # 清理题干
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

missing_opts = sum(1 for q in questions if not all([q['A'], q['B'], q['C'], q['D']]))
print(f"\n选项不完整: {missing_opts}道")

with open(r'D:\应用程序开发\刷题\prof_questions_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print("已保存")
