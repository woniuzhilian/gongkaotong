import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

def validate_json(filepath, name):
    print(f"\n{'='*60}")
    print(f"校验文件: {name}")
    print(f"路径: {filepath}")
    print(f"{'='*60}")

    errors = []
    warnings = []

    # 1. JSON语法合法
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[PASS] JSON语法合法，共{len(data)}道题")
    except json.JSONDecodeError as e:
        print(f"[FAIL] JSON语法错误: {e}")
        return
    except Exception as e:
        print(f"[FAIL] 读取失败: {e}")
        return

    required_fields = ['id', 'bigSubject', 'smallSubject', 'year', 'question', 'A', 'B', 'C', 'D', 'answer', 'analysis']
    valid_big_subjects = ['公共基础', '专业基础']
    valid_answers = ['A', 'B', 'C', 'D', '']

    # 统计
    field_missing = {}
    answer_invalid = []
    big_subject_invalid = []
    empty_question = []
    empty_analysis = []
    empty_options = []

    # id唯一性检查
    ids = set()
    duplicate_ids = []

    # HTML表格和LaTeX检查
    html_table_questions = []
    latex_questions = []
    img_tag_questions = []

    for i, q in enumerate(data):
        qid = q.get('id', f'index_{i}')

        # 3. 字段完整性
        for field in required_fields:
            if field not in q:
                if field not in field_missing:
                    field_missing[field] = []
                field_missing[field].append(qid)

        # 2. answer字段只有单个大写字母
        ans = q.get('answer', '')
        if ans not in valid_answers:
            answer_invalid.append((qid, ans))
        elif ans and len(ans) != 1:
            answer_invalid.append((qid, ans))

        # 4. bigSubject值
        bs = q.get('bigSubject', '')
        if bs not in valid_big_subjects:
            big_subject_invalid.append((qid, bs))

        # id唯一性
        if qid in ids:
            duplicate_ids.append(qid)
        ids.add(qid)

        # 空值检查
        if not q.get('question', '').strip():
            empty_question.append(qid)
        if not q.get('analysis', '').strip():
            empty_analysis.append(qid)
        for opt in ['A', 'B', 'C', 'D']:
            if not q.get(opt, '').strip():
                empty_options.append((qid, opt))

        # 6. HTML表格、LaTeX、配图标记检查
        qtext = q.get('question', '')
        if '<table' in qtext.lower() or '<tr' in qtext.lower() or '<td' in qtext.lower():
            html_table_questions.append(qid)
        if '$' in qtext:
            latex_questions.append(qid)
        if '【配图' in qtext or '【本题配图' in qtext:
            img_tag_questions.append(qid)

    # 输出结果
    print(f"\n--- 字段完整性 ---")
    if field_missing:
        for field, qids in field_missing.items():
            print(f"[FAIL] 字段'{field}'缺失: {len(qids)}道题 (id示例: {qids[:5]})")
            errors.append(f"字段'{field}'缺失{len(qids)}道")
    else:
        print(f"[PASS] 所有字段完整")

    print(f"\n--- answer字段 ---")
    if answer_invalid:
        print(f"[FAIL] answer格式错误: {len(answer_invalid)}道")
        for qid, ans in answer_invalid[:10]:
            print(f"  id={qid}: answer='{ans}'")
        errors.append(f"answer格式错误{len(answer_invalid)}道")
    else:
        print(f"[PASS] answer字段全部合法（单个大写字母或空）")

    print(f"\n--- bigSubject字段 ---")
    if big_subject_invalid:
        print(f"[FAIL] bigSubject值错误: {len(big_subject_invalid)}道")
        for qid, bs in big_subject_invalid[:5]:
            print(f"  id={qid}: bigSubject='{bs}'")
        errors.append(f"bigSubject值错误{len(big_subject_invalid)}道")
    else:
        bs_values = set(q.get('bigSubject', '') for q in data)
        print(f"[PASS] bigSubject值合法: {bs_values}")

    print(f"\n--- id唯一性 ---")
    if duplicate_ids:
        print(f"[FAIL] 重复id: {len(duplicate_ids)}个: {duplicate_ids[:10]}")
        errors.append(f"重复id {len(duplicate_ids)}个")
    else:
        print(f"[PASS] id全部唯一")

    print(f"\n--- 空值检查 ---")
    print(f"  题干为空: {len(empty_question)}道")
    print(f"  解析为空: {len(empty_analysis)}道")
    print(f"  选项为空: {len(empty_options)}个")
    if empty_question:
        warnings.append(f"题干为空{len(empty_question)}道")
    if empty_analysis:
        warnings.append(f"解析为空{len(empty_analysis)}道")

    print(f"\n--- HTML表格/LaTeX/配图 ---")
    print(f"  含HTML表格: {len(html_table_questions)}道")
    print(f"  含LaTeX公式($): {len(latex_questions)}道")
    print(f"  含配图标记: {len(img_tag_questions)}道")

    # 5. 抽查3道题
    print(f"\n--- 抽查3道题 ---")
    import random
    random.seed(42)
    sample_indices = random.sample(range(len(data)), min(3, len(data)))
    for idx in sample_indices:
        q = data[idx]
        print(f"\n  抽查 id={q.get('id')}:")
        print(f"    bigSubject: {q.get('bigSubject')}")
        print(f"    smallSubject: {q.get('smallSubject')}")
        print(f"    year: {q.get('year')}")
        print(f"    question: {q.get('question', '')[:80]}...")
        print(f"    A: {q.get('A', '')[:40]}")
        print(f"    B: {q.get('B', '')[:40]}")
        print(f"    C: {q.get('C', '')[:40]}")
        print(f"    D: {q.get('D', '')[:40]}")
        print(f"    answer: {q.get('answer')}")
        print(f"    analysis: {q.get('analysis', '')[:80]}...")

    # 汇总
    print(f"\n{'='*60}")
    print(f"校验汇总: {name}")
    print(f"  错误: {len(errors)}项")
    for e in errors:
        print(f"    - {e}")
    print(f"  警告: {len(warnings)}项")
    for w in warnings:
        print(f"    - {w}")
    if not errors:
        print(f"  结论: [PASS] 所有硬性检查通过")
    else:
        print(f"  结论: [FAIL] 存在错误，需修复")

    return data

# 校验公共基础
data1 = validate_json(r'D:\应用程序开发\刷题\all_questions_final.json', '公共基础')

# 校验专业基础
data2 = validate_json(r'D:\应用程序开发\刷题\prof_questions_final.json', '专业基础')

# 合并校验
print(f"\n{'='*60}")
print(f"两份题库合并统计")
print(f"{'='*60}")
print(f"公共基础: {len(data1)}道")
print(f"专业基础: {len(data2)}道")
print(f"总计: {len(data1) + len(data2)}道")

# 检查id是否各自独立
ids1 = set(q['id'] for q in data1)
ids2 = set(q['id'] for q in data2)
print(f"公共基础id范围: {min(ids1)}-{max(ids1)}")
print(f"专业基础id范围: {min(ids2)}-{max(ids2)}")
print(f"id重叠数: {len(ids1 & ids2)} (各自独立，重叠正常)")
