import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 创建2021-14题目对象
new_question = {
    "id": 153,
    "bigSubject": "公共基础",
    "smallSubject": "积分学",
    "year": "2021",
    "question": "设函数$f(u)$连续，而区域$D:x^2+y^2\\leq1$，且$x>0$，则二重积分$\\iint_D f(\\sqrt{x^2+y^2})dxdy$等于：（ ）。",
    "A": "$\\pi\\int_0^1 f(r)dr$",
    "B": "$\\pi\\int_0^1 rf(r)dr$",
    "C": "$\\frac{\\pi}{2}\\int_0^1 f(r)dr$",
    "D": "$\\frac{\\pi}{2}\\int_0^1 rf(r)dr$",
    "answer": "B",
    "analysis": "令$x=r\\cos\\theta$，$y=r\\sin\\theta$，则$0\\leq r\\leq1$，$-\\frac{\\pi}{2}\\leq\\theta\\leq\\frac{\\pi}{2}$，$x^2+y^2=r^2$，$dxdy\\rightarrow rdrd\\theta$，则$\\iint_D f(\\sqrt{x^2+y^2})dxdy=\\int_{-\\frac{\\pi}{2}}^{\\frac{\\pi}{2}}d\\theta\\int_0^1 f(r)rdr=\\pi\\int_0^1 rf(r)dr$，选B。"
}

# 找到插入位置：原来的id=153应该变成id=154
# 所有id >= 153的题目，id+1
for q in data:
    if q['id'] >= 153:
        q['id'] += 1

# 插入新题目
data.append(new_question)

# 按id重新排序
data.sort(key=lambda x: x['id'])

# 验证
print(f"补全前: 1437道题")
print(f"补全后: {len(data)}道题")
print(f"\nid=152: year={data[151]['year']}, {data[151]['smallSubject']}, {data[151]['question'][:50]}")
print(f"id=153: year={data[152]['year']}, {data[152]['smallSubject']}, {data[152]['question'][:50]}")
print(f"id=154: year={data[153]['year']}, {data[153]['smallSubject']}, {data[153]['question'][:50]}")

# 验证id=311现在对应什么
for q in data:
    if q['id'] == 312:  # 原来的311现在是312
        qclean = re.sub(r'【本题配图，PDF第\d+页】', '', q['question']).strip()
        print(f"\nid=312 (原311): year={q['year']}, {qclean[:60]}")
        break

# 保存
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n已保存更新后的JSON")
