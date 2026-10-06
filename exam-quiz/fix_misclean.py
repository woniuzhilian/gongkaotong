import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 修复id=706的D选项
data[705]['D'] = '访问控制与目录管理技术'
print(f"id=706 D选项已恢复: {data[705]['D']}")

# 清理id=1344的D选项
data[1343]['D'] = re.sub(r'\s*𝑋.*$', '', data[1343]['D']).strip()
print(f"id=1344 D选项已清理: {data[1343]['D']}")

# 保存
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已保存")
