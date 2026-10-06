import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 更新id=20的答案和解析
for q in data:
    if q['id'] == 20:
        q['answer'] = 'B'
        q['analysis'] = '此题是一道错题。双代号时标网络计划中：自由时差的值等于其波形线在坐标轴上的水平投影长度；工作总时差等于紧后工作总时差最小值与本工作自由时差值之和。B选项，工作自由时差为0，毫无疑问是对的。本工作自由时差为0，但其紧后工作总时差的情况不清楚，所以本工作总时差无法判断。因此，本工作是否是关键工作，总时差是否为0都不能判断，因此A和C错误。D选项，总时差最小值不会小于0，因此也是正确的。参考答案BD，本题取B。'
        print(f"已更新id=20: answer={q['answer']}")
        break

# 保存
with open(r'D:\应用程序开发\刷题\prof_questions_final_v2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 分批输出
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
    
    print(f"第{i+1}批: id {batch[0]['id']}-{batch[-1]['id']}, {len(batch)}题 -> {output_path}")

print(f"\n专业基础总计: {total}题, 分{batches}批输出")
