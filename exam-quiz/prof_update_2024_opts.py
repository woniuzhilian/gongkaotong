import sys, json, os, glob
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

img_dir = r'D:\应用程序开发\刷题\prof_option_images'

# 更新2024年的题目
updated = 0
for q in data:
    if q['year'] != '2024':
        continue
    
    qid = q['id']
    matches = glob.glob(os.path.join(img_dir, f'q{qid}_*.png'))
    if not matches:
        continue
    
    img_name = os.path.basename(matches[0])
    empty_opts = [opt for opt in ['A', 'B', 'C', 'D'] if q[opt] == '']
    
    if empty_opts:
        for opt in empty_opts:
            q[opt] = f'【见本题选项配图：{img_name}】'
        updated += 1
        print(f"id={qid}: 更新选项{empty_opts} -> {img_name}")

print(f"\n共更新{updated}道2024年题目")

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
    
    print(f"第{i+1}批: id {batch[0]['id']}-{batch[-1]['id']}, {len(batch)}题")

print(f"\n专业基础总计: {total}题, 分{batches}批")
