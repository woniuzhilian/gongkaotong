import json, re

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 清理analysis中的垃圾字符
for item in data:
    a = item['analysis']
    a = re.sub(r'第[一二三四五六七八九十]+章[\(（]?cid[:：].*?答案及解析\s*答案及解析', '', a)
    a = re.sub(r'[\(（]?cid[:：]\d+[\)）]?', '', a)
    a = re.sub(r'\(cid:\d+\)', '', a)
    a = a.strip()
    item['analysis'] = a

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

batch = data[:200]
with open(r'D:\应用程序开发\刷题\batch_1_compact.json', 'w', encoding='utf-8') as f:
    json.dump(batch, f, ensure_ascii=False, separators=(',', ':'))

print('修复完成')
print('第24题末尾:', data[23]['analysis'][-60:])
print('第116题末尾:', data[115]['analysis'][-60:])
