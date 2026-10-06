import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_questions_final.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# 确保字段顺序正确
fields = ['id', 'bigSubject', 'smallSubject', 'year', 'question', 'A', 'B', 'C', 'D', 'answer', 'analysis']

# 清理：确保answer只有单个字母
for q in questions:
    if q['answer']:
        q['answer'] = q['answer'][0].upper()
    # 确保所有字段存在
    for f in fields:
        if f not in q:
            q[f] = ''

# 分批输出，每批200题
batch_size = 200
total = len(questions)
batches = (total + batch_size - 1) // batch_size

print(f"总题目数: {total}, 分{batches}批输出")

for batch_idx in range(batches):
    start = batch_idx * batch_size
    end = min(start + batch_size, total)
    batch = questions[start:end]

    # 只保留指定字段
    output = []
    for q in batch:
        item = {f: q.get(f, '') for f in fields}
        output.append(item)

    # 输出JSON
    json_str = json.dumps(output, ensure_ascii=False, indent=2)
    print(f"\n=== 第{batch_idx+1}批 (id {batch[0]['id']}-{batch[-1]['id']}, 共{len(batch)}题) ===")
    print(json_str)

    # 同时保存到文件
    with open(rf'D:\应用程序开发\刷题\prof_batch_{batch_idx+1}.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
