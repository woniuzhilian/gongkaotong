import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_questions_final.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

fields = ['id', 'bigSubject', 'smallSubject', 'year', 'question', 'A', 'B', 'C', 'D', 'answer', 'analysis']

for q in questions:
    if q['answer']:
        q['answer'] = q['answer'][0].upper()
    for f in fields:
        if f not in q:
            q[f] = ''

batch_size = 200
total = len(questions)
batches = (total + batch_size - 1) // batch_size

for batch_idx in range(batches):
    start = batch_idx * batch_size
    end = min(start + batch_size, total)
    batch = questions[start:end]
    output = [{f: q.get(f, '') for f in fields} for q in batch]
    with open(rf'D:\应用程序开发\刷题\专业基础_第{batch_idx+1}批.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"第{batch_idx+1}批: id {batch[0]['id']}-{batch[-1]['id']}, {len(batch)}题")

print(f"完成，共{total}题，{batches}批")
