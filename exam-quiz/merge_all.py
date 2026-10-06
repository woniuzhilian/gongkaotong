import sys, json
sys.stdout.reconfigure(encoding='utf-8')

# 读取公共基础
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    pub = json.load(f)

# 读取专业基础（分批）
prof = []
for i in range(1, 4):
    with open(rf'D:\应用程序开发\刷题\专业基础_第{i}批.json', 'r', encoding='utf-8') as f:
        prof.extend(json.load(f))

print(f"公共基础: {len(pub)}题, id范围 {pub[0]['id']}-{pub[-1]['id']}")
print(f"专业基础: {len(prof)}题, id范围 {prof[0]['id']}-{prof[-1]['id']}")

# 合并（公共基础在前，专业基础在后，各自id独立）
merged = pub + prof
print(f"合并后: {len(merged)}题")

# 验证id独立性
pub_ids = set(q['id'] for q in pub)
prof_ids = set(q['id'] for q in prof)
print(f"公共基础id数: {len(pub_ids)}, 专业基础id数: {len(prof_ids)}")
print(f"id重叠数: {len(pub_ids & prof_ids)} (允许重叠，因bigSubject不同)")

# 保存合并文件
with open(r'D:\应用程序开发\刷题\all_questions_merged.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"\n已保存: all_questions_merged.json")
