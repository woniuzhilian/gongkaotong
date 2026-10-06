import sys, json, re
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_merged_full.json', 'r', encoding='utf-8') as f:
    full_data = json.load(f)

# 找出选项为空的题目
empty_opt_questions = []
for q in full_data:
    empty_opts = [opt for opt in ['A', 'B', 'C', 'D'] if q[opt] == '']
    if empty_opts:
        empty_opt_questions.append({
            'id': q['id'],
            'year': q['year'],
            'qnum': q['_qnum'],
            'empty_opts': empty_opts,
            'question': q['question'][:60]
        })

print(f"共{len(empty_opt_questions)}道题选项为空")

# 对于2016-2023年的题目，在试题册中定位页码
q_pdf = r'D:\证件相关\一级岩土工程师\真题空白卷\岩土专业基础历年真题试题册（2024版）.pdf'
doc = pymupdf.open(q_pdf)

# 建立年份到起始页的映射
year_pages = {}
current_year = None
for i in range(len(doc)):
    text = doc[i].get_text()
    # 匹配年份标题
    m = re.search(r'(\d{4})\s*年（补考）\s*注册岩土专业基础真题', text)
    if m:
        year_pages[m.group(1) + '补'] = i
        current_year = m.group(1) + '补'
    else:
        m = re.search(r'(\d{4})\s*年\s*注册岩土专业基础真题', text)
        if m:
            year_pages[m.group(1)] = i
            current_year = m.group(1)

print("\n年份起始页:")
for y, p in sorted(year_pages.items()):
    print(f"  {y}: 第{p+1}页")

# 对每道题，在对应年份的页面范围内查找
print("\n定位题目页码:")
question_locations = {}
for q in empty_opt_questions:
    year = q['year']
    qnum = q['qnum']
    if year == '2024':
        continue  # 2024年不在这个PDF中
    
    if year not in year_pages:
        print(f"  id={q['id']}: 年份{year}未找到起始页")
        continue
    
    start_page = year_pages[year]
    # 找下一个年份的起始页
    next_years = [p for y, p in year_pages.items() if p > start_page]
    end_page = min(next_years) if next_years else len(doc)
    
    # 在页面范围内查找题号
    found = False
    for pg in range(start_page, end_page):
        text = doc[pg].get_text()
        # 匹配题号模式 "24、"
        pattern = rf'(?:^|\n){qnum}[、.．]'
        if re.search(pattern, text):
            question_locations[q['id']] = (pg, year, qnum)
            found = True
            break
    
    if not found:
        print(f"  id={q['id']}, {year}年第{qnum}题: 未找到")

print(f"\n成功定位{len(question_locations)}道题")
doc.close()

# 保存定位信息
with open(r'D:\应用程序开发\刷题\prof_opt_locations.json', 'w', encoding='utf-8') as f:
    json.dump({str(k): v for k, v in question_locations.items()}, f, ensure_ascii=False, indent=2)
