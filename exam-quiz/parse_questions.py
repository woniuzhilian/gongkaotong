import pdfplumber
import re
import json
from collections import OrderedDict

# ============================================================
# 1. 检测题目PDF中每页的图片，记录有图片的页码
# ============================================================
def detect_images(pdf_path):
    """检测每页是否有图片，返回有图片的页码集合"""
    image_pages = set()
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if page.images:
                image_pages.add(i + 1)
    return image_pages

print("检测题目PDF中的图片...")
q_image_pages = detect_images(r'D:\应用程序开发\刷题\题目和答案pdf\公共基础分类版真题详解（13~24）_题目.pdf')
print(f"有图片的页码: {sorted(q_image_pages)}")
print(f"共 {len(q_image_pages)} 页有图片")

# ============================================================
# 2. 读取提取的文本
# ============================================================
with open(r'D:\应用程序开发\刷题\questions_raw.txt', 'r', encoding='utf-8') as f:
    q_raw = f.read()
with open(r'D:\应用程序开发\刷题\answers_raw.txt', 'r', encoding='utf-8') as f:
    a_raw = f.read()

# ============================================================
# 3. 解析题目PDF
# ============================================================

# 章节映射：章节名 -> 小科目名
# 先构建章节列表
chapter_pattern = re.compile(r'^第[一二三四五六七八九十]+章\s+(.+)$', re.MULTILINE)

def parse_questions(raw_text, image_pages):
    """解析题目文本，返回题目列表"""
    lines = raw_text.split('\n')
    questions = []
    current_chapter = ""
    current_page = 0
    current_part = ""
    
    # 题目标记正则
    q_mark_pattern = re.compile(r'【(\d{4}\s*补?)-(\d+)】')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 检测页码
        page_match = re.match(r'===PAGE_(\d+)===', line)
        if page_match:
            current_page = int(page_match.group(1))
            i += 1
            continue
        
        # 检测部分标题
        part_match = re.match(r'第[一二三四五六七八九十]+部分\s+(.+)', line)
        if part_match and '...' not in line:
            current_part = part_match.group(1).strip()
            i += 1
            continue
        
        # 检测章节标题
        chap_match = re.match(r'第[一二三四五六七八九十]+章\s+(.+)', line)
        if chap_match and '...' not in line:
            current_chapter = chap_match.group(1).strip()
            i += 1
            continue
        
        # 检测题目标记
        mark_match = q_mark_pattern.search(line)
        if mark_match:
            year_raw = mark_match.group(1).replace(' ', '')
            q_num = mark_match.group(2)
            qid = f"{year_raw}-{q_num}"
            
            # 收集这道题的所有文本，直到下一个题目标记或章节标题
            q_lines = []
            # 先把当前行标记之后的内容加入
            mark_end = mark_match.end()
            first_line_content = line[mark_end:].strip()
            if first_line_content:
                q_lines.append(first_line_content)
            
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                # 检测页码
                pm = re.match(r'===PAGE_(\d+)===', next_line)
                if pm:
                    current_page = int(pm.group(1))
                    i += 1
                    continue
                # 检测下一个题目标记
                if q_mark_pattern.search(next_line):
                    break
                # 检测章节/部分标题
                if re.match(r'第[一二三四五六七八九十]+[章部分]\s+', next_line) and '...' not in next_line:
                    break
                # 跳过空行但保留
                if next_line:
                    q_lines.append(next_line)
                i += 1
            
            q_text = ' '.join(q_lines)
            
            # 解析选项
            options = {'A': '', 'B': '', 'C': '', 'D': ''}
            question_text = q_text
            
            # 尝试分割选项 （A）...（B）...（C）...（D）...
            # 选项可能是（A）或(A) 或 A. 等格式
            opt_pattern = re.compile(r'[（(]\s*([A-D])\s*[）)]')
            opt_matches = list(opt_pattern.finditer(q_text))
            
            if len(opt_matches) >= 2:
                # 题干是第一个选项之前的内容
                question_text = q_text[:opt_matches[0].start()].strip()
                # 提取每个选项
                for idx, om in enumerate(opt_matches):
                    opt_letter = om.group(1)
                    start = om.end()
                    end = opt_matches[idx+1].start() if idx+1 < len(opt_matches) else len(q_text)
                    options[opt_letter] = q_text[start:end].strip()
            
            # 检测当前页是否有图片（粗略判断：如果题目所在页有图片，则标记）
            has_image = current_page in image_pages
            
            questions.append({
                'qid': qid,
                'year': year_raw,
                'smallSubject': current_chapter,
                'question': question_text,
                'A': options['A'],
                'B': options['B'],
                'C': options['C'],
                'D': options['D'],
                'page': current_page,
                'has_image_hint': has_image
            })
        else:
            i += 1
    
    return questions

print("\n解析题目...")
questions = parse_questions(q_raw, q_image_pages)
print(f"解析到 {len(questions)} 道题")

# 去重：保留第一次出现的
seen_qids = set()
unique_questions = []
for q in questions:
    if q['qid'] not in seen_qids:
        seen_qids.add(q['qid'])
        unique_questions.append(q)
print(f"去重后 {len(unique_questions)} 道题")

# ============================================================
# 4. 解析答案PDF
# ============================================================
def parse_answers(raw_text):
    """解析答案文本，返回答案字典 {qid: {answer, analysis}}"""
    lines = raw_text.split('\n')
    answers = {}
    current_page = 0
    
    q_mark_pattern = re.compile(r'【(\d{4}\s*补?)-(\d+)】')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 检测页码
        page_match = re.match(r'===PAGE_(\d+)===', line)
        if page_match:
            current_page = int(page_match.group(1))
            i += 1
            continue
        
        # 检测题目标记
        mark_match = q_mark_pattern.search(line)
        if mark_match:
            year_raw = mark_match.group(1).replace(' ', '')
            q_num = mark_match.group(2)
            qid = f"{year_raw}-{q_num}"
            
            # 收集答案文本
            a_lines = []
            mark_end = mark_match.end()
            first_line_content = line[mark_end:].strip()
            if first_line_content:
                a_lines.append(first_line_content)
            
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                pm = re.match(r'===PAGE_(\d+)===', next_line)
                if pm:
                    current_page = int(pm.group(1))
                    i += 1
                    continue
                if q_mark_pattern.search(next_line):
                    break
                if re.match(r'第[一二三四五六七八九十]+[章部分]\s+', next_line) and '...' not in next_line:
                    break
                # 跳过(cid:xxx)垃圾字符行
                if next_line and not re.match(r'^[\(（]?cid[:：]', next_line):
                    a_lines.append(next_line)
                i += 1
            
            a_text = ' '.join(a_lines)
            
            # 提取答案
            answer = ''
            ans_match = re.search(r'答案[:：]\s*([A-D])', a_text)
            if ans_match:
                answer = ans_match.group(1)
            
            # 提取解析（去掉答案行和考点分析行的标签，保留内容）
            analysis = a_text
            # 去掉"答案：X"
            analysis = re.sub(r'答案[:：]\s*[A-D]\s*', '', analysis)
            # 去掉【考点分析】标签但保留内容
            analysis = re.sub(r'【考点分析】', '', analysis)
            # 去掉【解析】标签但保留内容
            analysis = re.sub(r'【解析】', '', analysis)
            analysis = analysis.strip()
            
            if qid not in answers:
                answers[qid] = {'answer': answer, 'analysis': analysis}
        else:
            i += 1
    
    return answers

print("\n解析答案...")
answers = parse_answers(a_raw)
print(f"解析到 {len(answers)} 道题答案")

# ============================================================
# 5. 合并并输出
# ============================================================
print("\n合并题目和答案...")
result = []
for idx, q in enumerate(unique_questions):
    qid = q['qid']
    ans = answers.get(qid, {'answer': '', 'analysis': ''})
    
    # 处理图片标记
    question = q['question']
    if q['has_image_hint']:
        question = f"【本题配图，PDF第{q['page']}页】{question}"
    
    item = {
        'id': idx + 1,
        'bigSubject': '公共基础',
        'smallSubject': q['smallSubject'],
        'year': q['year'],
        'question': question,
        'A': q['A'],
        'B': q['B'],
        'C': q['C'],
        'D': q['D'],
        'answer': ans['answer'],
        'analysis': ans['analysis']
    }
    result.append(item)

print(f"最终合并 {len(result)} 道题")

# 保存完整结果到文件（供分批输出使用）
with open(r'D:\应用程序开发\刷题\all_questions.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("已保存到 all_questions.json")

# 打印前3题预览
print("\n=== 前3题预览 ===")
for item in result[:3]:
    print(json.dumps(item, ensure_ascii=False, indent=2))
    print()
