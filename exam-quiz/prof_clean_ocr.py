import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 清理 ===PAGE_XXX=== 格式的OCR残留
# 模式：===PAGE_数字=== 后面可能跟数字
pattern = re.compile(r'===PAGE_\d+===\s*\d*')

cleaned_count = 0
for q in data:
    for field in ['question', 'A', 'B', 'C', 'D', 'analysis']:
        val = q.get(field, '')
        if val:
            new_val = pattern.sub('', val)
            # 清理残留的 === 标记
            new_val = re.sub(r'=+', '', new_val)
            # 清理多余空格
            new_val = re.sub(r'\s+', ' ', new_val).strip()
            if new_val != val:
                q[field] = new_val
                cleaned_count += 1

print(f"清理了{cleaned_count}处OCR残留")

# 再次检查
remaining = 0
for q in data:
    for field in ['question', 'A', 'B', 'C', 'D', 'analysis']:
        if '===PAGE' in q.get(field, '') or '===' in q.get(field, ''):
            remaining += 1
            print(f"  残留: id={q['id']}, {field}: {q[field][:50]}")

print(f"剩余残留: {remaining}处")

# 保存
with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 重新分批输出
batch_size = 200
total = len(data)
batches = (total + batch_size - 1) // batch_size

for i in range(batches):
    start = i * batch_size
    end = min(start + batch_size, total)
    batch = data[start:end]
    output_path = rf'D:\应用程序开发\刷题\专业基础_第{i+1}批.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)

print(f"\n已重新分批输出，共{total}题，{batches}批")
