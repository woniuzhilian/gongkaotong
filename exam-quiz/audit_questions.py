import json, re, os, sys

with open('exam-quiz/src/data/questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

print(f"总题数: {len(questions)}\n")

issues = []

# 1. 字段完整性检查
for q in questions:
    qid = q.get('id', '?')
    year = q.get('year', '?')
    yq = q.get('yearQnum', '?')
    bs = q.get('bigSubject', '?')
    label = f"[{bs} {year}-{yq} id={qid}]"

    for field in ['question', 'A', 'B', 'C', 'D', 'answer', 'analysis']:
        val = q.get(field)
        if val is None:
            issues.append(('MISSING_FIELD', label, f"缺少字段: {field}"))
        elif val == '':
            issues.append(('EMPTY_FIELD', label, f"字段为空: {field}"))

    if not q.get('bigSubject'):
        issues.append(('MISSING_FIELD', label, "缺少 bigSubject"))
    if not q.get('smallSubject'):
        issues.append(('MISSING_FIELD', label, "缺少 smallSubject"))
    if not q.get('year'):
        issues.append(('MISSING_FIELD', label, "缺少 year"))

# 2. 公式配对检查 ($...$ 奇数个$号)
for q in questions:
    qid = q.get('id', '?')
    year = q.get('year', '?')
    yq = q.get('yearQnum', '?')
    bs = q.get('bigSubject', '?')
    label = f"[{bs} {year}-{yq} id={qid}]"

    for field in ['question', 'A', 'B', 'C', 'D', 'analysis']:
        text = q.get(field, '') or ''
        dollar_count = text.count('$')
        if dollar_count % 2 != 0:
            issues.append(('ODD_DOLLAR', label, f"{field}: $号数量为奇数({dollar_count}), 公式可能未闭合"))

        # 检查空公式 $$
        empty_formulas = re.findall(r'\$\s*\$', text)
        if empty_formulas:
            issues.append(('EMPTY_FORMULA', label, f"{field}: 发现空公式 ${{}}  {len(empty_formulas)} 处"))

        # 检查未闭合的公式（$后面没有匹配的$直到行尾）
        # 更细致的检查：提取所有$...$公式，看是否有异常
        formulas = re.findall(r'\$([^$]+)\$', text)
        for fm in formulas:
            # 检查公式内是否有明显的截断（以反斜杠结尾表示命令未完成）
            if fm.rstrip().endswith('\\'):
                issues.append(('TRUNCATED_FORMULA', label, f"{field}: 公式可能截断: $...{fm[-20:]}\\$"))

# 3. 配图引用检查
img_dir = 'exam-quiz/public/images'
existing_images = set()
if os.path.isdir(img_dir):
    existing_images = set(os.listdir(img_dir))

for q in questions:
    qid = q.get('id', '?')
    year = q.get('year', '?')
    yq = q.get('yearQnum', '?')
    bs = q.get('bigSubject', '?')
    label = f"[{bs} {year}-{yq} id={qid}]"

    for field in ['question', 'A', 'B', 'C', 'D', 'analysis']:
        text = q.get(field, '') or ''
        # 查找 img 标签
        img_tags = re.findall(r'<img[^>]+src="([^"]+)"[^>]*>', text)
        for src in img_tags:
            # 提取文件名
            fname = src.split('/')[-1]
            if fname and fname not in existing_images:
                issues.append(('MISSING_IMAGE', label, f"{field}: 引用图片不存在: {fname}"))

        # 也检查纯文本形式的图片引用如 [图片] 或 如图
        if '[图片]' in text or '[图]' in text:
            issues.append(('IMAGE_PLACEHOLDER', label, f"{field}: 包含图片占位符文本"))

# 4. 特殊符号问题检查
problematic_patterns = [
    (r'\\frac\{[^}]*\}$', 'TRUNCATED_FRAC', '公式中 \\frac 可能截断'),
    (r'\\sqrt\{[^}]*$', 'TRUNCATED_SQRT', '公式中 \\sqrt 可能截断'),
    (r'\\[a-zA-Z]+$', 'TRUNCATED_CMD', 'LaTeX命令可能截断'),
]

for q in questions:
    qid = q.get('id', '?')
    year = q.get('year', '?')
    yq = q.get('yearQnum', '?')
    bs = q.get('bigSubject', '?')
    label = f"[{bs} {year}-{yq} id={qid}]"

    for field in ['question', 'A', 'B', 'C', 'D', 'analysis']:
        text = q.get(field, '') or ''
        # 检查常见的乱码/替换符号
        if '□' in text or '■' in text or '●' in text:
            issues.append(('SPECIAL_CHAR', label, f"{field}: 包含特殊符号 □■●"))
        if '' in text:
            issues.append(('BROKEN_CHAR', label, f"{field}: 包含乱码字符(U+FFFD)"))
        # 检查常见的OCR错误模式
        if re.search(r'[a-zA-Z]\d+[a-zA-Z]?\b', text) and not re.search(r'\$.*\d', text):
            # 可能是上下标未转换，如 x2 应该是 x^2
            pass  # 太宽泛，跳过

# 5. 上下标问题检查 - 检查非公式区域内的数字上下标
for q in questions:
    qid = q.get('id', '?')
    year = q.get('year', '?')
    yq = q.get('yearQnum', '?')
    bs = q.get('bigSubject', '?')
    label = f"[{bs} {year}-{yq} id={qid}]"

    for field in ['question', 'A', 'B', 'C', 'D', 'analysis']:
        text = q.get(field, '') or ''
        # 移除公式部分，检查纯文本中的上下标问题
        pure_text = re.sub(r'\$[^$]+\$', '', text)
        # 检查 Unicode 上下标字符
        sub_chars = '₀₁₂₃₄₅₆₇₈₉'
        sup_chars = '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻'
        for c in sub_chars + sup_chars:
            if c in pure_text:
                issues.append(('UNICODE_SUBSUP', label, f"{field}: 纯文本中包含Unicode上下标字符 '{c}'"))

# 6. 答案格式检查
for q in questions:
    qid = q.get('id', '?')
    year = q.get('year', '?')
    yq = q.get('yearQnum', '?')
    bs = q.get('bigSubject', '?')
    label = f"[{bs} {year}-{yq} id={qid}]"
    ans = q.get('answer', '')
    if ans and ans not in ('A', 'B', 'C', 'D'):
        issues.append(('BAD_ANSWER', label, f"答案格式异常: '{ans}'"))

# 7. 内容过短检查（可能是截断）
for q in questions:
    qid = q.get('id', '?')
    year = q.get('year', '?')
    yq = q.get('yearQnum', '?')
    bs = q.get('bigSubject', '?')
    label = f"[{bs} {year}-{yq} id={qid}]"

    qtext = q.get('question', '') or ''
    if len(qtext) < 5:
        issues.append(('TOO_SHORT', label, f"题干过短({len(qtext)}字): '{qtext}'"))

    for field in ['A', 'B', 'C', 'D']:
        opt = q.get(field, '') or ''
        if opt == '':
            pass  # 已在EMPTY_FIELD中报告

    analysis = q.get('analysis', '') or ''
    if len(analysis) < 3 and len(analysis) > 0:
        issues.append(('SHORT_ANALYSIS', label, f"解析过短({len(analysis)}字): '{analysis}'"))

# 8. 检查 HTML 标签问题
for q in questions:
    qid = q.get('id', '?')
    year = q.get('year', '?')
    yq = q.get('yearQnum', '?')
    bs = q.get('bigSubject', '?')
    label = f"[{bs} {year}-{yq} id={qid}]"

    for field in ['question', 'A', 'B', 'C', 'D', 'analysis']:
        text = q.get(field, '') or ''
        # 检查未闭合的HTML标签
        open_tags = re.findall(r'<(table|tr|td|th|img|br|hr)\b', text)
        close_tags = re.findall(r'</(table|tr|td|th)>', text)
        # table/tr/td 需要闭合
        for tag in ['table', 'tr', 'td', 'th']:
            o = len(re.findall(f'<{tag}[\\s>]', text))
            c = len(re.findall(f'</{tag}>', text))
            if o != c:
                issues.append(('HTML_MISMATCH', label, f"{field}: <{tag}> 开{o}个 闭{c}个 不匹配"))

        # 检查自闭合img标签是否正确
        imgs = re.findall(r'<img[^>]*>', text)
        for img in imgs:
            if not img.endswith('/>') and not img.endswith('>'):
                issues.append(('BAD_IMG_TAG', label, f"{field}: img标签格式异常"))

# 9. 检查重复id
ids = [q.get('id') for q in questions]
from collections import Counter
dup_ids = {k: v for k, v in Counter(ids).items() if v > 1}
for did, cnt in dup_ids.items():
    issues.append(('DUP_ID', f"[id={did}]", f"id重复 {cnt} 次"))

# 10. 检查公式中常见的KaTeX不支持命令
katex_problematic = [
    (r'\\begin\{(matrix|pmatrix|bmatrix|vmatrix|cases|aligned|gathered)\}', None),  # these are supported
]
# 检查可能不支持的命令
for q in questions:
    qid = q.get('id', '?')
    year = q.get('year', '?')
    yq = q.get('yearQnum', '?')
    bs = q.get('bigSubject', '?')
    label = f"[{bs} {year}-{yq} id={qid}]"

    for field in ['question', 'A', 'B', 'C', 'D', 'analysis']:
        text = q.get(field, '') or ''
        formulas = re.findall(r'\$([^$]+)\$', text)
        for fm in formulas:
            # 检查大括号不匹配
            open_b = fm.count('{')
            close_b = fm.count('}')
            if open_b != close_b:
                issues.append(('BRACE_MISMATCH', label, f"{field}: 公式大括号不匹配 {{={open_b} }}={close_b}"))

# ===== 输出汇总 =====
# 按类型分组
from collections import defaultdict
by_type = defaultdict(list)
for itype, label, desc in issues:
    by_type[itype].append((label, desc))

print("=" * 70)
print("问题汇总")
print("=" * 70)

type_names = {
    'MISSING_FIELD': '缺少必要字段',
    'EMPTY_FIELD': '字段内容为空',
    'ODD_DOLLAR': '公式$号未闭合(奇数个)',
    'EMPTY_FORMULA': '空公式',
    'TRUNCATED_FORMULA': '公式可能截断',
    'MISSING_IMAGE': '引用图片文件不存在',
    'IMAGE_PLACEHOLDER': '图片占位符文本',
    'SPECIAL_CHAR': '特殊符号',
    'BROKEN_CHAR': '乱码字符',
    'UNICODE_SUBSUP': 'Unicode上下标字符(非公式区)',
    'BAD_ANSWER': '答案格式异常',
    'TOO_SHORT': '题干过短(可能截断)',
    'SHORT_ANALYSIS': '解析过短',
    'HTML_MISMATCH': 'HTML标签不匹配',
    'BAD_IMG_TAG': 'img标签格式异常',
    'DUP_ID': 'ID重复',
    'BRACE_MISMATCH': '公式大括号不匹配',
}

total = 0
for itype in sorted(by_type.keys()):
    items = by_type[itype]
    name = type_names.get(itype, itype)
    print(f"\n### {name} ({len(items)}处)")
    for label, desc in items[:50]:  # 每类最多显示50条
        print(f"  {label} {desc}")
    if len(items) > 50:
        print(f"  ... 还有 {len(items) - 50} 处")
    total += len(items)

print(f"\n{'=' * 70}")
print(f"共发现 {total} 处问题，涉及 {len(set(label for _, (label, _) in [(t, i) for t, i in [(k, v) for k, vs in by_type.items() for v in vs]])])} 道题")
print(f"{'=' * 70}")
