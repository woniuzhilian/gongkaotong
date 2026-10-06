import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

img_dir = r'D:\应用程序开发\刷题\prof_option_images'

# 更新2016-2023年的题目
updated = 0
for q in data:
    qid = q['id']
    img_file = f'q{qid}_*.png'
    
    # 查找对应的图片文件
    import glob
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

print(f"\n共更新{updated}道题")

# 保存
with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已保存")
