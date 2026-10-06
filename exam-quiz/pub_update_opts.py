import sys, json, os, glob
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

img_dir = r'D:\应用程序开发\刷题\pub_option_images'

updated = 0
for q in data:
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

print(f"共更新{updated}道题")

# 验证空选项
empty_count = 0
for q in data:
    for opt in ['A', 'B', 'C', 'D']:
        if q[opt] == '':
            empty_count += 1
print(f"剩余空选项: {empty_count}个")

# 保存
with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已保存 all_questions_final.json")
