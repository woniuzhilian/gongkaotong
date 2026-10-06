import pdfplumber
import re
import json

# ============================================================
# 读取文本
# ============================================================
with open(r'D:\应用程序开发\刷题\questions_raw.txt', 'r', encoding='utf-8') as f:
    q_raw = f.read()
with open(r'D:\应用程序开发\刷题\answers_raw.txt', 'r', encoding='utf-8') as f:
    a_raw = f.read()

q_lines = q_raw.split('\n')
a_lines = a_raw.split('\n')

q_mark_pattern = re.compile(r'【(\d{4}\s*补?)-(\d+)】')
opt_pattern = re.compile(r'[（(]\s*([A-D])\s*[）)]')
chapter_pattern = re.compile(r'^第[一二三四五六七八九十]+章\s+(.+)$')

# ============================================================
# 公式LaTeX转换
# ============================================================
SUP_MAP = {'⁰':'^0','¹':'^1','²':'^2','³':'^3','⁴':'^4','⁵':'^5',
           '⁶':'^6','⁷':'^7','⁸':'^8','⁹':'^9','⁺':'^+','⁻':'^-','⁼':'^=',
           '⁽':'^(','⁾':'^)','ⁿ':'^n'}
SUB_MAP = {'₀':'_0','₁':'_1','₂':'_2','₃':'_3','₄':'_4','₅':'_5',
           '₆':'_6','₇':'_7','₈':'_8','₉':'_9','₊':'_+','₋':'_-','₌':'_=',
           '₍':'_(','₎':'_)'}

def convert_math_to_latex(text):
    """将文本中的数学符号做基本LaTeX转换，并用$ $包裹公式段"""
    if not text:
        return text
    
    # 上标下标转换
    for k, v in SUP_MAP.items():
        text = text.replace(k, v)
    for k, v in SUB_MAP.items():
        text = text.replace(k, v)
    
    # 识别连续的数学公式区域并用$ $包裹
    # 数学字符集：希腊字母、数学运算符、拉丁字母斜体、数字、常用数学符号
    math_chars = (
        r'𝐀-𝐙𝐚-𝐳𝔄-𝔇𝔉-𝔶'  # 数学斜体
        r'Α-Ωα-ω'  # 希腊字母
        r'∀-⋿'  # 数学运算符
        r'−±×÷=≠≈≤≥<>→←↑↓'
        r'√∑∏∫∂∇∞π'
        r'𝑎-𝑧𝐴-𝑍'  # 数学斜体字母
        r'𝛼-𝜔𝚨-𝛀'  # 数学斜体希腊
        r'𝒜-𝒵𝒶-𝓏'
        r'0-9\.\,\;\:\(\)\[\]\{\}\/\+\-\*\^\|\\'
        r' _'
    )
    
    # 找包含数学字符且长度>=3的连续片段，用$ $包裹
    # 但要避免把普通文本也包进去
    # 策略：找连续的"高数学密度"区域
    result = text
    # 简单处理：将包含特定数学符号的子串用$包裹
    # 这里不做过度处理，保留原始文本结构
    
    return text

# ============================================================
# 建立行号->章节映射
# ============================================================
def build_chapter_map(lines):
    chap_map = {}
    current_chapter = ""
    for i, line in enumerate(lines):
        l = line.strip()
        if re.match(r'===PAGE_(\d+)===', l):
            chap_map[i] = current_chapter
            continue
        m = chapter_pattern.match(l)
        if m and '...' not in l:
            current_chapter = m.group(1).strip()
        chap_map[i] = current_chapter
    return chap_map

q_chap_map = build_chapter_map(q_lines)

# ============================================================
# 检测图片页
# ============================================================
def detect_image_pages(pdf_path):
    image_pages = set()
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if page.images:
                image_pages.add(i + 1)
    return image_pages

q_image_pages = detect_image_pages(r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf')

# ============================================================
# 找到所有题目标记行号
# ============================================================
q_mark_lines = [i for i, line in enumerate(q_lines) if q_mark_pattern.search(line)]
a_mark_lines = [i for i, line in enumerate(a_lines) if q_mark_pattern.search(line)]

print(f"题目: {len(q_mark_lines)} 标记, 答案: {len(a_mark_lines)} 标记")

# ============================================================
# 解析题目（基于行边界，保留换行）
# ============================================================
def get_page_at_line(lines, line_idx):
    for j in range(line_idx, -1, -1):
        m = re.match(r'===PAGE_(\d+)===', lines[j].strip())
        if m:
            return int(m.group(1))
    return 0

def has_chinese(s):
    return bool(re.search(r'[\u4e00-\u9fff]', s))

def parse_one_question(lines, mark_idx, next_mark_idx, chap_map, image_pages):
    line = lines[mark_idx].strip()
    mark_match = q_mark_pattern.search(line)
    year_raw = mark_match.group(1).replace(' ', '')
    q_num = mark_match.group(2)
    qid = f"{year_raw}-{q_num}"
    page = get_page_at_line(lines, mark_idx)
    chapter = chap_map.get(mark_idx, "")
    
    # 收集行，保留原始行结构
    collected = []
    for j in range(mark_idx, next_mark_idx):
        l = lines[j].strip()
        if re.match(r'===PAGE_(\d+)===', l):
            continue
        if chapter_pattern.match(l) and '...' not in l and j > mark_idx:
            break
        if l:
            collected.append(l)
    
    if not collected:
        return None
    
    # 第一行去掉标记
    first = collected[0]
    mark_end = mark_match.end()
    first_rest = first[mark_end:].strip()
    
    # 用换行符合并，保留行边界
    full_text = first_rest
    if len(collected) > 1:
        full_text += '\n' + '\n'.join(collected[1:])
    
    # 找选项位置（在整个文本中）
    opt_matches = list(opt_pattern.finditer(full_text))
    
    question_text = full_text.replace('\n', ' ').strip()
    options = {'A': '', 'B': '', 'C': '', 'D': ''}
    
    if len(opt_matches) >= 2:
        # 题干 = 第一个选项之前的内容，换行替换为空格
        question_text = full_text[:opt_matches[0].start()].replace('\n', ' ').strip()
        
        for oi, om in enumerate(opt_matches):
            letter = om.group(1)
            start = om.end()
            if oi + 1 < len(opt_matches):
                end = opt_matches[oi + 1].start()
            else:
                end = len(full_text)
            
            raw_content = full_text[start:end]
            
            if letter == 'D':
                # D选项截断：基于行边界
                # D选项内容中，第一个换行之后的内容如果是纯数学（无中文），
                # 且不是D选项的明确延续（如括号、方程组），则截断
                nl_pos = raw_content.find('\n')
                if nl_pos > 0:
                    before_nl = raw_content[:nl_pos].strip()
                    after_nl = raw_content[nl_pos+1:].strip()
                    # 如果换行后是纯数学，且before_nl不以特定延续符号结尾
                    if after_nl and not has_chinese(after_nl):
                        # 检查before_nl是否以未闭合的括号或特定符号结尾
                        ends_with_continuation = bool(re.search(r'[\(\[\{=,，、]$', before_nl))
                        if not ends_with_continuation:
                            raw_content = before_nl
                        # else: 保留多行内容
                    # 如果换行后有中文，保留（可能是D选项的文字延续）
                # 去掉多余换行
                content = raw_content.replace('\n', ' ').strip()
            else:
                content = raw_content.replace('\n', ' ').strip()
            
            options[letter] = content
    
    # 公式转换
    question_text = convert_math_to_latex(question_text)
    for k in options:
        options[k] = convert_math_to_latex(options[k])
    
    # 图片标记
    if page in image_pages and re.search(r'[如图所示图中下图上图]', question_text):
        question_text = f"【本题配图，PDF第{page}页】{question_text}"
    
    return {
        'qid': qid,
        'year': year_raw,
        'smallSubject': chapter,
        'question': question_text,
        'A': options['A'],
        'B': options['B'],
        'C': options['C'],
        'D': options['D'],
    }

print("解析题目...")
questions = []
for idx, mark_idx in enumerate(q_mark_lines):
    next_idx = q_mark_lines[idx + 1] if idx + 1 < len(q_mark_lines) else len(q_lines)
    q = parse_one_question(q_lines, mark_idx, next_idx, q_chap_map, q_image_pages)
    if q:
        questions.append(q)

# 去重
seen = set()
unique_questions = []
for q in questions:
    if q['qid'] not in seen:
        seen.add(q['qid'])
        unique_questions.append(q)
print(f"题目: {len(questions)} -> 去重后 {len(unique_questions)}")

# ============================================================
# 解析答案
# ============================================================
def parse_one_answer(lines, mark_idx, next_mark_idx):
    line = lines[mark_idx].strip()
    mark_match = q_mark_pattern.search(line)
    year_raw = mark_match.group(1).replace(' ', '')
    q_num = mark_match.group(2)
    qid = f"{year_raw}-{q_num}"
    
    collected = []
    for j in range(mark_idx, next_mark_idx):
        l = lines[j].strip()
        if re.match(r'===PAGE_(\d+)===', l):
            continue
        if chapter_pattern.match(l) and '...' not in l and j > mark_idx:
            break
        if re.match(r'^[\(（]?cid[:：]', l):
            continue
        if l:
            collected.append(l)
    
    if not collected:
        return qid, '', ''
    
    first = collected[0]
    mark_end = mark_match.end()
    rest = first[mark_end:].strip()
    full_text = rest
    if len(collected) > 1:
        full_text += ' ' + ' '.join(collected[1:])
    
    answer = ''
    ans_match = re.search(r'答案[:：]\s*([A-D])', full_text)
    if ans_match:
        answer = ans_match.group(1)
    
    analysis = full_text
    analysis = re.sub(r'答案[:：]\s*[A-D]\s*', '', analysis)
    analysis = re.sub(r'【考点分析】', '', analysis)
    analysis = re.sub(r'【解析】', '', analysis)
    analysis = analysis.strip()
    analysis = convert_math_to_latex(analysis)
    
    return qid, answer, analysis

print("解析答案...")
answers = {}
for idx, mark_idx in enumerate(a_mark_lines):
    next_idx = a_mark_lines[idx + 1] if idx + 1 < len(a_mark_lines) else len(a_lines)
    qid, ans, ana = parse_one_answer(a_lines, mark_idx, next_idx)
    if qid and qid not in answers:
        answers[qid] = {'answer': ans, 'analysis': ana}
print(f"答案: {len(answers)}")

# ============================================================
# 合并
# ============================================================
result = []
for idx, q in enumerate(unique_questions):
    qid = q['qid']
    ans = answers.get(qid, {'answer': '', 'analysis': ''})
    result.append({
        'id': idx + 1,
        'bigSubject': '公共基础',
        'smallSubject': q['smallSubject'],
        'year': q['year'],
        'question': q['question'],
        'A': q['A'],
        'B': q['B'],
        'C': q['C'],
        'D': q['D'],
        'answer': ans['answer'],
        'analysis': ans['analysis']
    })

print(f"最终 {len(result)} 道题")

with open(r'D:\应用程序开发\刷题\all_questions.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 预览前10题
print("\n=== 前10题 ===")
for item in result[:10]:
    print(f"[{item['id']}] {item['year']} | {item['smallSubject'][:15]} | ans={item['answer']}")
    print(f"  Q: {item['question'][:65]}")
    print(f"  A: {item['A'][:35]} | B: {item['B'][:35]}")
    print(f"  C: {item['C'][:35]} | D: {item['D'][:35]}")
    print()

# 统计D选项可能有问题的（长度>40且无中文标点）
bad_d = sum(1 for r in result if len(r['D']) > 40 and not re.search(r'[。？！，]', r['D']))
print(f"D选项可能异常的题数: {bad_d}")
