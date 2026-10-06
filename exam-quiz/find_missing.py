import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\应用程序开发\刷题\prof_answers_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 搜索2018-19和2017-40附近的内容
for keyword in ['2018-19', '2017-40', '2018-20', '2017-39']:
    idx = text.find(keyword)
    if idx >= 0:
        print(f"找到 '{keyword}' at {idx}:")
        print(text[idx:idx+200])
        print("---")
    else:
        print(f"未找到 '{keyword}'")
        # 搜索类似的
        for m in re.finditer(r'【\s*2018\s*-\s*1\d\s*】', text):
            print(f"  类似: {m.group(0)} at {m.start()}")
        for m in re.finditer(r'【\s*2017\s*-\s*[34]\d\s*】', text):
            print(f"  类似: {m.group(0)} at {m.start()}")
