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
# 1. 建立行号 -> 章节名映射
# ============================================================
def build_chapter_map(lines):
    """返回每个行号对应的章节名（取该行之前最近的章节标题）"""
    chap_map = {}
    current_chapter = ""
    for i, line in enumerate(lines):
        l = line.strip()
        # 跳过页码
        if re.match(r'===PAGE_(\d+)===', l):
            chap_map[i] = current_chapter
            continue
        m = chapter_pattern.match(l)
        if m and '...' not in l:
            current_chapter = m.group(1).strip()
        chap_map[i] = current_chapter
    return chap_map

q_chap_map = build_chapter_map(q_lines)
print("章节映射建立完成")

# ============================================================
# 2. 检测图片页
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
# 3. 找到所有题目标记行号
# ============================================================
q_mark_lines = []
for i, line in enumerate(q_lines):
    if q_mark_pattern.search(line):
        q_mark_lines.append(i)

print(f"题目PDF: {len(q_mark_lines)} 个题目标记")

a_mark_lines = []
for i, line in enumerate(a_lines):
    if q_mark_pattern.search(line):
        a_mark_lines.append(i)

print(f"答案PDF: {len(a_mark_lines)} 个题目标记")

# ============================================================
# 4. 解析题目
# ============================================================
def get_page_at_line(lines, line_idx):
    """获取某行所在的PDF页码"""
    for j in range(line_idx, -1, -1):
        m = re.match(r'===PAGE_(\d+)===', lines[j].strip())
        if m:
            return int(m.group(1))
    return 0

def parse_one_question(lines, mark_idx, next_mark_idx, chap_map, image_pages):
    """解析单道题"""
    line = lines[mark_idx].strip()
    mark_match = q_mark_pattern.search(line)
    year_raw = mark_match.group(1).replace(' ', '')
    q_num = mark_match.group(2)
    qid = f"{year_raw}-{q_num}"
    
    page = get_page_at_line(lines, mark_idx)
    chapter = chap_map.get(mark_idx, "")
    
    # 收集行：从标记行到下一题标记行（不含），跳过页码和章节标题
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
    
    # 第一行：去掉标记
    first = collected[0]
    mark_end = mark_match.end()
    rest = first[mark_end:].strip()
    
    # 合并所有文本
    full_text = rest
    if len(collected) > 1:
        full_text += ' ' + ' '.join(collected[1:])
    
    # 找选项位置
    opt_matches = list(opt_pattern.finditer(full_text))
    
    question_text = full_text
    options = {'A': '', 'B': '', 'C': '', 'D': ''}
    
    if len(opt_matches) >= 2:
        # 题干
        question_text = full_text[:opt_matches[0].start()].strip()
        
        # 提取选项
        for oi, om in enumerate(opt_matches):
            letter = om.group(1)
            start = om.end()
            if oi + 1 < len(opt_matches):
                end = opt_matches[oi + 1].start()
            else:
                end = len(full_text)
            content = full_text[start:end].strip()
            
            # D选项截断策略：
            # 如果D选项后还有大量纯数学内容，可能是下一题的公式前缀
            # 策略：找D选项中第一个中文标点；如果没有，找第一个"看起来像结束"的位置
            if letter == 'D':
                # 找中文句号/问号/叹号
                pm = re.search(r'[。？！]', content)
                if pm:
                    content = content[:pm.end()].strip()
                else:
                    # 没有中文标点，可能是纯数学选项
                    # 如果内容很长且包含多个空格分隔的片段，可能混入了下一题
                    # 简单策略：如果D选项超过80字符，截断到第一个合理位置
                    if len(content) > 80:
                        # 找前80字符内最后一个空格
                        cut = content[:80].rfind(' ')
                        if cut > 20:
                            content = content[:cut].strip()
            
            options[letter] = content
    
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

print("\n解析题目...")
questions = []
for idx, mark_idx in enumerate(q_mark_lines):
    next_idx = q_mark_lines[idx + 1] if idx + 1 < len(q_mark_lines) else len(q_lines)
    q = parse_one_question(q_lines, mark_idx, next_idx, q_chap_map, q_image_pages)
    if q:
        questions.append(q)

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
# 5. 解析答案
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
    
    return qid, answer, analysis

print("\n解析答案...")
answers = {}
for idx, mark_idx in enumerate(a_mark_lines):
    next_idx = a_mark_lines[idx + 1] if idx + 1 < len(a_mark_lines) else len(a_lines)
    qid, ans, ana = parse_one_answer(a_lines, mark_idx, next_idx)
    if qid and qid not in answers:
        answers[qid] = {'answer': ans, 'analysis': ana}

print(f"解析到 {len(answers)} 道题答案")

# ============================================================
# 6. 合并
# ============================================================
print("\n合并...")
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
print("\n=== 前10题预览 ===")
for item in result[:10]:
    print(f"[{item['id']}] {item['year']} | {item['smallSubject']} | ans={item['answer']}")
    print(f"  Q: {item['question'][:70]}")
    print(f"  A: {item['A'][:40]} | B: {item['B'][:40]}")
    print(f"  C: {item['C'][:40]} | D: {item['D'][:40]}")
    print()
