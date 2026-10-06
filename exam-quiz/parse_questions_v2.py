import pdfplumber
import re
import json

# ============================================================
# 工具函数
# ============================================================

def has_chinese(s):
    """判断字符串是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', s))

def normalize_formula(text):
    """将Unicode数学字符做基本LaTeX转换，并用$ $包裹公式段"""
    # 这个函数处理连续的数学符号区域
    # 先不做复杂转换，保留原始字符，后续统一处理
    return text

def unicode_sup_to_latex(s):
    """上标Unicode转LaTeX"""
    sup_map = {'⁰':'^0','¹':'^1','²':'^2','³':'^3','⁴':'^4','⁵':'^5',
               '⁶':'^6','⁷':'^7','⁸':'^8','⁹':'^9','⁺':'^+','⁻':'^-','⁼':'^=',
               '⁽':'^(','⁾':'^)','ⁿ':'^n'}
    for k, v in sup_map.items():
        s = s.replace(k, v)
    return s

def unicode_sub_to_latex(s):
    """下标Unicode转LaTeX"""
    sub_map = {'₀':'_0','₁':'_1','₂':'_2','₃':'_3','₄':'_4','₅':'_5',
               '₆':'_6','₇':'_7','₈':'_8','₉':'_9','₊':'_+','₋':'_-','₌':'_=',
               '₍':'_(','₎':'_)'}
    for k, v in sub_map.items():
        s = s.replace(k, v)
    return s

# ============================================================
# 1. 检测题目PDF中每页的图片位置
# ============================================================
def detect_image_pages(pdf_path):
    image_pages = set()
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if page.images:
                image_pages.add(i + 1)
    return image_pages

print("检测图片页...")
q_image_pages = detect_image_pages(r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf')

# ============================================================
# 2. 读取文本
# ============================================================
with open(r'D:\应用程序开发\刷题\questions_raw.txt', 'r', encoding='utf-8') as f:
    q_raw = f.read()
with open(r'D:\应用程序开发\刷题\answers_raw.txt', 'r', encoding='utf-8') as f:
    a_raw = f.read()

# ============================================================
# 3. 改进的题目解析：基于行的分析
# ============================================================

q_mark_pattern = re.compile(r'【(\d{4}\s*补?)-(\d+)】')
opt_pattern = re.compile(r'[（(]\s*([A-D])\s*[）)]')

def parse_questions_v2(raw_text, image_pages):
    lines = raw_text.split('\n')
    questions = []
    current_chapter = ""
    current_page = 0
    current_part = ""
    
    # 第一遍：找到所有题目标记所在的行号
    mark_line_indices = []
    for i, line in enumerate(lines):
        if q_mark_pattern.search(line):
            mark_line_indices.append(i)
    
    print(f"找到 {len(mark_line_indices)} 个题目标记行")
    
    # 第二遍：逐题解析
    for idx, mark_line_idx in enumerate(mark_line_indices):
        line = lines[mark_line_idx].strip()
        mark_match = q_mark_pattern.search(line)
        if not mark_match:
            continue
        
        year_raw = mark_match.group(1).replace(' ', '')
        q_num = mark_match.group(2)
        qid = f"{year_raw}-{q_num}"
        
        # 确定这道题的行范围：从当前标记行到下一个标记行之前
        end_idx = mark_line_indices[idx + 1] if idx + 1 < len(mark_line_indices) else len(lines)
        
        # 收集这道题的所有行（跳过页码标记行）
        q_lines = []
        page_at_mark = current_page
        for j in range(mark_line_idx, end_idx):
            l = lines[j].strip()
            pm = re.match(r'===PAGE_(\d+)===', l)
            if pm:
                current_page = int(pm.group(1))
                if j == mark_line_idx:
                    page_at_mark = current_page
                continue
            # 检测章节/部分标题（不是目录行）
            if re.match(r'第[一二三四五六七八九十]+[章部分]\s+', l) and '...' not in l:
                if j > mark_line_idx:
                    # 遇到新章节，停止收集
                    break
                else:
                    current_chapter = re.match(r'第[一二三四五六七八九十]+章\s+(.+)', l).group(1).strip() if re.match(r'第[一二三四五六七八九十]+章\s+', l) else current_chapter
                    continue
            if l:
                q_lines.append(l)
        
        # 现在 q_lines 是这道题的所有文本行
        # 第一行包含题目标记和题干开头
        first_line = q_lines[0]
        mark_end = mark_match.end()
        question_starter = first_line[mark_end:].strip()
        
        # 合并所有行
        full_text = question_starter
        if len(q_lines) > 1:
            full_text += ' ' + ' '.join(q_lines[1:])
        
        # 解析选项
        options = {'A': '', 'B': '', 'C': '', 'D': ''}
        question_text = full_text
        
        opt_matches = list(opt_pattern.finditer(full_text))
        
        if len(opt_matches) >= 2:
            # 题干 = 第一个选项之前
            question_text = full_text[:opt_matches[0].start()].strip()
            
            # 提取每个选项
            for oi, om in enumerate(opt_matches):
                opt_letter = om.group(1)
                start = om.end()
                if oi + 1 < len(opt_matches):
                    end = opt_matches[oi + 1].start()
                else:
                    end = len(full_text)
                opt_content = full_text[start:end].strip()
                
                # 对于D选项，需要截断：如果D选项之后包含下一题的公式前缀
                # 策略：D选项中如果出现多个空格分隔的数学片段，且没有中文连接词，
                # 则可能混入了下一题内容。但很难精确判断。
                # 改进：D选项只取到第一个句号或合理结束点
                if opt_letter == 'D':
                    # 找D选项中的第一个中文句号或问号
                    period_match = re.search(r'[。？！]', opt_content)
                    if period_match:
                        opt_content = opt_content[:period_match.end()].strip()
                
                options[opt_letter] = opt_content
        
        # 检测图片：如果题干包含"如图"、"图"、"所示"等关键词且该页有图片
        has_image = False
        if page_at_mark in image_pages:
            if re.search(r'[如图图所示图中下图上图]', question_text):
                has_image = True
        
        if has_image:
            question_text = f"【本题配图，PDF第{page_at_mark}页】{question_text}"
        
        questions.append({
            'qid': qid,
            'year': year_raw,
            'smallSubject': current_chapter,
            'question': question_text,
            'A': options['A'],
            'B': options['B'],
            'C': options['C'],
            'D': options['D'],
            'page': page_at_mark,
        })
    
    return questions

print("\n解析题目（v2）...")
questions = parse_questions_v2(q_raw, q_image_pages)
print(f"解析到 {len(questions)} 道题")

# 去重
seen = set()
unique_questions = []
for q in questions:
    if q['qid'] not in seen:
        seen.add(q['qid'])
        unique_questions.append(q)
print(f"去重后 {len(unique_questions)} 道题")

# ============================================================
# 4. 答案解析
# ============================================================
def parse_answers_v2(raw_text):
    lines = raw_text.split('\n')
    answers = {}
    current_page = 0
    
    mark_line_indices = []
    for i, line in enumerate(lines):
        if q_mark_pattern.search(line):
            mark_line_indices.append(i)
    
    for idx, mark_line_idx in enumerate(mark_line_indices):
        line = lines[mark_line_idx].strip()
        mark_match = q_mark_pattern.search(line)
        if not mark_match:
            continue
        
        year_raw = mark_match.group(1).replace(' ', '')
        q_num = mark_match.group(2)
        qid = f"{year_raw}-{q_num}"
        
        end_idx = mark_line_indices[idx + 1] if idx + 1 < len(mark_line_indices) else len(lines)
        
        a_lines = []
        for j in range(mark_line_idx, end_idx):
            l = lines[j].strip()
            pm = re.match(r'===PAGE_(\d+)===', l)
            if pm:
                current_page = int(pm.group(1))
                continue
            if re.match(r'第[一二三四五六七八九十]+[章部分]\s+', l) and '...' not in l:
                if j > mark_line_idx:
                    break
                continue
            # 跳过cid垃圾行
            if re.match(r'^[\(（]?cid[:：]', l):
                continue
            if l:
                a_lines.append(l)
        
        first_line = a_lines[0] if a_lines else ''
        mark_end = mark_match.end()
        starter = first_line[mark_end:].strip() if mark_end < len(first_line) else ''
        full_text = starter
        if len(a_lines) > 1:
            full_text += ' ' + ' '.join(a_lines[1:])
        
        # 提取答案
        answer = ''
        ans_match = re.search(r'答案[:：]\s*([A-D])', full_text)
        if ans_match:
            answer = ans_match.group(1)
        
        # 提取解析
        analysis = full_text
        analysis = re.sub(r'答案[:：]\s*[A-D]\s*', '', analysis)
        analysis = re.sub(r'【考点分析】', '', analysis)
        analysis = re.sub(r'【解析】', '', analysis)
        analysis = analysis.strip()
        
        if qid not in answers:
            answers[qid] = {'answer': answer, 'analysis': analysis}
    
    return answers

print("\n解析答案...")
answers = parse_answers_v2(a_raw)
print(f"解析到 {len(answers)} 道题答案")

# ============================================================
# 5. 合并
# ============================================================
print("\n合并...")
result = []
for idx, q in enumerate(unique_questions):
    qid = q['qid']
    ans = answers.get(qid, {'answer': '', 'analysis': ''})
    
    item = {
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
    }
    result.append(item)

print(f"最终 {len(result)} 道题")

with open(r'D:\应用程序开发\刷题\all_questions.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 预览前5题
print("\n=== 前5题预览 ===")
for item in result[:5]:
    print(f"id={item['id']}, qid对应={item['year']}, small={item['smallSubject']}")
    print(f"  Q: {item['question'][:80]}...")
    print(f"  A: {item['A'][:50]}")
    print(f"  B: {item['B'][:50]}")
    print(f"  C: {item['C'][:50]}")
    print(f"  D: {item['D'][:50]}")
    print(f"  answer: {item['answer']}")
    print()
