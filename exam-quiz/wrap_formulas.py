import json
import re

with open(r'D:\应用程序开发\刷题\all_questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 数学字母数字符号区块 U+1D400-U+1D7FF
# 数学运算符 U+2200-U+22FF
# 常用数学符号
def is_math_char(c):
    cp = ord(c)
    # 数学字母数字符号
    if 0x1D400 <= cp <= 0x1D7FF:
        return True
    # 数学运算符
    if 0x2200 <= cp <= 0x22FF:
        return True
    # 希腊字母
    if 0x0370 <= cp <= 0x03FF:
        return True
    # 常用符号
    if c in '+-*/=<>()[]{}|√∞π∑∏∫∂∇±×÷≠≈≤≥→←↑↓−·…':
        return True
    # 数字和点
    if c.isdigit() or c in '.,;:':
        return True
    # 空格
    if c in ' \t':
        return True
    return False

def wrap_formulas(text):
    """将文本中的连续数学公式区域用$ $包裹"""
    if not text:
        return text
    
    result = []
    i = 0
    n = len(text)
    
    while i < n:
        c = text[i]
        # 检查是否是数学字符（且不是中文）
        if is_math_char(c) and not re.match(r'[\u4e00-\u9fff]', c):
            # 找到连续的数学区域
            j = i
            has_math_alpha = False
            while j < n:
                cj = text[j]
                if is_math_char(cj) and not re.match(r'[\u4e00-\u9fff]', cj):
                    if 0x1D400 <= ord(cj) <= 0x1D7FF or 0x0370 <= ord(cj) <= 0x03FF:
                        has_math_alpha = True
                    j += 1
                else:
                    break
            
            segment = text[i:j]
            # 只有包含数学字母/希腊字母，且长度>=2的区域才包裹
            if has_math_alpha and len(segment.strip()) >= 2:
                result.append('$' + segment.strip() + '$')
            else:
                result.append(segment)
            i = j
        else:
            result.append(c)
            i += 1
    
    return ''.join(result)

# 对所有题的题干、选项、解析做公式包裹
print("处理公式包裹...")
for item in data:
    item['question'] = wrap_formulas(item['question'])
    item['A'] = wrap_formulas(item['A'])
    item['B'] = wrap_formulas(item['B'])
    item['C'] = wrap_formulas(item['C'])
    item['D'] = wrap_formulas(item['D'])
    item['analysis'] = wrap_formulas(item['analysis'])

# 保存
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 预览前3题
print("\n=== 前3题预览 ===")
for item in data[:3]:
    print(json.dumps(item, ensure_ascii=False, indent=2))
    print()

print(f"共 {len(data)} 题")
