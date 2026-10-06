import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

updates = {
    1044: {  # 2016-94 数字电子技术 JK触发器
        'answer': 'A',
        'analysis': '从图上可以看出是下降沿触发的JK触发器，RD为异步清零，低电平有效，所以在第一个下降沿时，Q为0，A为1，经过与门，J为0，K为0，所以保持原来状态0，第二个下降沿时，Q为0，所以J还是0，K为0，所以Q的状态还是0。'
    },
    1221: {  # 2021-98 计算机系统 存储器
        'answer': 'A',
        'analysis': '目前微机系统内常用的外存储器为硬盘存储器，A正确。'
    },
    850: {  # 2022-71 流体静力学
        'answer': 'D',
        'analysis': '分析可知水银和水的分界面处为等压面，标记为1-1等压面，水银柱液面高差为h\'。由于题目问的是计示压强，因此本题的压强均用相对压强表示。P计=γ汞h\'-γ水h2-γ油h1=(13.6×0.5−0.6−0.85×0.4)γ水=5.86×9800=57428pa。'
    }
}

for q in data:
    if q['id'] in updates:
        q['answer'] = updates[q['id']]['answer']
        q['analysis'] = updates[q['id']]['analysis']
        print(f"已更新 id={q['id']} ({q['year']}-{q['smallSubject']}): answer={q['answer']}")

with open(r'D:\应用程序开发\刷题\all_questions_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n更新完成，文件已保存。")
