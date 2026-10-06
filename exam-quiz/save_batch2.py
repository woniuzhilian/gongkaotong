import sys, json
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8'))
batch = [q for q in data if 201 <= q['id'] <= 400]
print('批次数量:', len(batch))
print('id范围:', batch[0]['id'], '-', batch[-1]['id'])
json.dump(batch, open(r'D:\应用程序开发\刷题\batch_2_compact.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('已保存到 batch_2_compact.json')
