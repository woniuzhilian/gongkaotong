import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    pub = json.load(f)

with open(r'D:\应用程序开发\刷题\questions_raw.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

# 找出空选项的题目
empty_opt_questions = []
for q in pub:
    empty_opts = [opt for opt in ['A', 'B', 'C', 'D'] if q[opt] == '']
    if empty_opts:
        empty_opt_questions.append(q)

print(f"共{len(empty_opt_questions)}道题有空选项")

# 分类统计
math_count = 0
graph_count = 0
other_count = 0

for q in empty_opt_questions:
    question = q['question']
    # 判断是否是数学题（含LaTeX公式）
    if '$' in question or any(kw in question for kw in ['积分', '导数', '微分', '矩阵', '行列式', '概率', '向量', '级数', '极限', '方程']):
        math_count += 1
    elif any(kw in question for kw in ['波形', '电路', '应力状态', '压杆', '挠曲线', '截面', '图形', '如图', '图示']):
        graph_count += 1
    else:
        other_count += 1

print(f"数学公式选项: {math_count}道")
print(f"图形选项: {graph_count}道")
print(f"其他: {other_count}道")

# 查看几道数学题的原始文本
print("\n=== 数学题原始文本示例 ===")
for q in empty_opt_questions[:3]:
    qid = q['id']
    # 在原始文本中查找这道题
    # 用题干前20字搜索
    search_text = q['question'][:20].replace('$', '').replace(' ', '')
    idx = raw_text.find(search_text)
    if idx > 0:
        # 显示后面300字
        snippet = raw_text[idx:idx+300]
        print(f"\nid={qid}: {q['question'][:50]}")
        print(f"原始文本: {snippet[:200]}")
