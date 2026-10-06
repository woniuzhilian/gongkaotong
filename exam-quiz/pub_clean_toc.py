import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 检查目录残留
dirty_count = 0
for q in data:
    for field in ['question', 'A', 'B', 'C', 'D', 'analysis']:
        val = q.get(field, '')
        # 检查是否包含"目录"、"第一"等目录残留
        if '目录' in val or '第一部分' in val or '第二部分' in val:
            dirty_count += 1
            print(f"id={q['id']}, {field}: {val[-50:]}")

print(f"\n共{dirty_count}处目录残留")

# 清理目录残留
cleaned = 0
for q in data:
    for field in ['question', 'A', 'B', 'C', 'D', 'analysis']:
        val = q.get(field, '')
        if val:
            # 去掉末尾的目录残留
            new_val = re.sub(r'\s*目\s*录.*$', '', val)
            new_val = re.sub(r'\s*第[一二三四五六七八九十]+部分.*$', '', new_val)
            if new_val != val:
                q[field] = new_val.strip()
                cleaned += 1

print(f"清理了{cleaned}处目录残留")

# 保存
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已保存")
