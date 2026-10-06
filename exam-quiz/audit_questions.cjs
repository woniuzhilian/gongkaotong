const fs = require('fs');
const path = require('path');

const data = JSON.parse(fs.readFileSync('exam-quiz/src/data/questions.json', 'utf-8'));
console.log(`总题数: ${data.length}\n`);

const issues = [];
const imgDir = 'exam-quiz/public/images';
let existingImages = new Set();
if (fs.existsSync(imgDir)) {
  existingImages = new Set(fs.readdirSync(imgDir));
}

function label(q) {
  return `[${q.bigSubject || '?'} ${q.year || '?'}-${q.yearQnum || '?'} id=${q.id || '?'}]`;
}

// 1. 字段完整性
for (const q of data) {
  const lb = label(q);
  for (const f of ['question', 'A', 'B', 'C', 'D', 'answer', 'analysis', 'bigSubject', 'smallSubject', 'year']) {
    if (q[f] === undefined || q[f] === null) {
      issues.push(['MISSING_FIELD', lb, `缺少字段: ${f}`]);
    } else if (typeof q[f] === 'string' && q[f].trim() === '') {
      issues.push(['EMPTY_FIELD', lb, `字段为空: ${f}`]);
    }
  }
}

// 2. 公式$号配对
for (const q of data) {
  const lb = label(q);
  for (const f of ['question', 'A', 'B', 'C', 'D', 'analysis']) {
    const text = q[f] || '';
    const cnt = (text.match(/\$/g) || []).length;
    if (cnt % 2 !== 0) {
      issues.push(['ODD_DOLLAR', lb, `${f}: $号奇数(${cnt}), 公式未闭合`]);
    }
    // 空公式
    const emptyF = text.match(/\$\s*\$/g);
    if (emptyF) {
      issues.push(['EMPTY_FORMULA', lb, `${f}: 空公式 ${emptyF.length} 处`]);
    }
  }
}

// 3. 公式大括号配对
for (const q of data) {
  const lb = label(q);
  for (const f of ['question', 'A', 'B', 'C', 'D', 'analysis']) {
    const text = q[f] || '';
    const formulas = [];
    const re = /\$([^$]+)\$/g;
    let m;
    while ((m = re.exec(text)) !== null) formulas.push(m[1]);
    for (const fm of formulas) {
      const ob = (fm.match(/\{/g) || []).length;
      const cb = (fm.match(/\}/g) || []).length;
      if (ob !== cb) {
        issues.push(['BRACE_MISMATCH', lb, `${f}: 公式大括号不匹配 {=${ob} }=${cb}, 公式片段: ...${fm.substring(Math.max(0, Math.max(fm.indexOf('{'), fm.indexOf('}')) - 15))}...`]);
      }
    }
  }
}

// 4. 配图引用检查
for (const q of data) {
  const lb = label(q);
  for (const f of ['question', 'A', 'B', 'C', 'D', 'analysis']) {
    const text = q[f] || '';
    const imgTags = text.match(/<img[^>]+src="([^"]+)"[^>]*>/g) || [];
    for (const tag of imgTags) {
      const srcMatch = tag.match(/src="([^"]+)"/);
      if (srcMatch) {
        const fname = srcMatch[1].split('/').pop();
        if (fname && !existingImages.has(fname)) {
          issues.push(['MISSING_IMAGE', lb, `${f}: 图片不存在: ${fname}`]);
        }
      }
    }
    if (text.includes('[图片]') || text.includes('[图]')) {
      issues.push(['IMAGE_PLACEHOLDER', lb, `${f}: 包含图片占位符`]);
    }
  }
}

// 5. 特殊符号/乱码
for (const q of data) {
  const lb = label(q);
  for (const f of ['question', 'A', 'B', 'C', 'D', 'analysis']) {
    const text = q[f] || '';
    if (text.includes('')) {
      issues.push(['BROKEN_CHAR', lb, `${f}: 包含乱码字符(U+FFFD)`]);
    }
    // Unicode上下标（非公式区）
    const pureText = text.replace(/\$[^$]+\$/g, '');
    const subChars = '₀₁₂₃₄₅₆₇₈₉';
    const supChars = '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻';
    for (const c of subChars + supChars) {
      if (pureText.includes(c)) {
        issues.push(['UNICODE_SUBSUP', lb, `${f}: 纯文本含Unicode上下标 '${c}'`]);
        break; // 只报一次
      }
    }
  }
}

// 6. 答案格式
for (const q of data) {
  const lb = label(q);
  const ans = q.answer || '';
  if (ans && !['A', 'B', 'C', 'D'].includes(ans)) {
    issues.push(['BAD_ANSWER', lb, `答案格式异常: '${ans}'`]);
  }
}

// 7. 内容过短
for (const q of data) {
  const lb = label(q);
  const qt = q.question || '';
  if (qt.length < 5) {
    issues.push(['TOO_SHORT_Q', lb, `题干过短(${qt.length}字): '${qt}'`]);
  }
  const an = q.analysis || '';
  if (an.length > 0 && an.length < 3) {
    issues.push(['SHORT_ANALYSIS', lb, `解析过短(${an.length}字): '${an}'`]);
  }
}

// 8. HTML标签匹配
for (const q of data) {
  const lb = label(q);
  for (const f of ['question', 'A', 'B', 'C', 'D', 'analysis']) {
    const text = q[f] || '';
    for (const tag of ['table', 'tr', 'td', 'th']) {
      const o = (text.match(new RegExp(`<${tag}[\\s>]`, 'g')) || []).length;
      const c = (text.match(new RegExp(`</${tag}>`, 'g')) || []).length;
      if (o !== c) {
        issues.push(['HTML_MISMATCH', lb, `${f}: <${tag}> 开${o}个 闭${c}个`]);
      }
    }
  }
}

// 9. 重复ID
const idCounts = {};
for (const q of data) {
  const id = q.id;
  idCounts[id] = (idCounts[id] || 0) + 1;
}
for (const [id, cnt] of Object.entries(idCounts)) {
  if (cnt > 1) {
    issues.push(['DUP_ID', `[id=${id}]`, `id重复 ${cnt} 次`]);
  }
}

// 10. 检查公式中可能的截断（以\结尾或命令不完整）
for (const q of data) {
  const lb = label(q);
  for (const f of ['question', 'A', 'B', 'C', 'D', 'analysis']) {
    const text = q[f] || '';
    const re = /\$([^$]+)\$/g;
    let m;
    while ((m = re.exec(text)) !== null) {
      const fm = m[1];
      // 检查连续的反斜杠命令是否完整
      if (/\\[a-zA-Z]+\s*$/.test(fm) && !/\\(alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|omega|sum|prod|int|lim|sin|cos|tan|log|ln|exp|max|min|sup|inf|pm|times|div|cdot|leq|geq|neq|approx|infty|rightarrow|leftarrow|Rightarrow|Leftarrow|forall|exists|in|notin|subset|supset|cup|cap|vee|wedge|oplus|otimes|perp|angle|triangle|square|circ|bullet|star|dagger|ldots|cdots|vdots|ddots|hat|bar|tilde|vec|dot|ddot|over|under|frac|sqrt|left|right|big|Big|text|mathrm|mathbf|mathit|mathcal|mathbb|begin|end|array|matrix|pmatrix|bmatrix|vmatrix|cases|aligned|gathered)\b/.test(fm)) {
        // 可能是截断的命令 - 只检查非常见命令
      }
    }
  }
}

// 11. 检查选项之间内容完全相同（可能是数据错误）
for (const q of data) {
  const lb = label(q);
  const opts = ['A', 'B', 'C', 'D'].map(k => q[k] || '');
  for (let i = 0; i < 4; i++) {
    for (let j = i + 1; j < 4; j++) {
      if (opts[i] && opts[i] === opts[j]) {
        issues.push(['DUP_OPTIONS', lb, `选项${String.fromCharCode(65+i)}和${String.fromCharCode(65+j)}内容完全相同: "${opts[i].substring(0, 30)}..."`]);
      }
    }
  }
}

// 12. 检查题干或选项中包含 "如图" 但没有配图
for (const q of data) {
  const lb = label(q);
  for (const f of ['question', 'A', 'B', 'C', 'D']) {
    const text = q[f] || '';
    if (/如图所示|如(图|下图)所示|见(图|下图)/.test(text)) {
      const hasImg = /<img/.test(text);
      if (!hasImg) {
        issues.push(['MISSING_IMG_REF', lb, `${f}: 提到"如图"但未包含图片`]);
      }
    }
  }
}

// 13. 检查纯文本中的上下标问题 - 如 x2 应该是 x^2, H2O 等
for (const q of data) {
  const lb = label(q);
  for (const f of ['question', 'A', 'B', 'C', 'D', 'analysis']) {
    const text = q[f] || '';
    const pureText = text.replace(/\$[^$]+\$/g, '');
    // 化学式: 字母+数字 如 H2O, Ca(OH)2, Na2SO4
    const chemMatches = pureText.matchAll(/([A-Z][a-z]?)\d/g);
    for (const cm of chemMatches) {
      // 排除常见的非化学式（如 2013年 等）
      const before = pureText.substring(Math.max(0, cm.index - 2), cm.index);
      if (/\d/.test(before)) continue; // 前面是数字，可能是年份等
      issues.push(['CHEM_SUBSCRIPT', lb, `${f}: 化学式下标未转LaTeX: '${cm[0]}'`]);
    }
  }
}

// ===== 汇总输出 =====
const byType = {};
for (const [type, lb, desc] of issues) {
  if (!byType[type]) byType[type] = [];
  byType[type].push([lb, desc]);
}

const typeNames = {
  MISSING_FIELD: '缺少必要字段',
  EMPTY_FIELD: '字段内容为空',
  ODD_DOLLAR: '公式$号未闭合(奇数个)',
  EMPTY_FORMULA: '空公式($$)',
  BRACE_MISMATCH: '公式大括号不匹配',
  MISSING_IMAGE: '引用图片文件不存在',
  IMAGE_PLACEHOLDER: '图片占位符文本',
  BROKEN_CHAR: '乱码字符(U+FFFD)',
  UNICODE_SUBSUP: 'Unicode上下标(非公式区)',
  BAD_ANSWER: '答案格式异常(非ABCD)',
  TOO_SHORT_Q: '题干过短(可能截断)',
  SHORT_ANALYSIS: '解析过短',
  HTML_MISMATCH: 'HTML标签开闭不匹配',
  DUP_ID: 'ID重复',
  DUP_OPTIONS: '选项内容完全相同',
  MISSING_IMG_REF: '提到"如图"但无配图',
  CHEM_SUBSCRIPT: '化学式下标未转LaTeX',
};

console.log('='.repeat(70));
console.log('题库数据问题汇总');
console.log('='.repeat(70));

let total = 0;
const affectedQs = new Set();
for (const type of Object.keys(byType).sort()) {
  const items = byType[type];
  const name = typeNames[type] || type;
  console.log(`\n### ${name} (${items.length}处)`);
  for (const [lb, desc] of items.slice(0, 80)) {
    console.log(`  ${lb} ${desc}`);
    affectedQs.add(lb);
  }
  if (items.length > 80) {
    console.log(`  ... 还有 ${items.length - 80} 处`);
  }
  total += items.length;
}

console.log(`\n${'='.repeat(70)}`);
console.log(`共发现 ${total} 处问题，涉及约 ${affectedQs.size} 道题（总题数 ${data.length}）`);
console.log(`${'='.repeat(70)}`);

// 额外统计
console.log('\n--- 题库基本统计 ---');
const pubQ = data.filter(q => q.bigSubject === '公共基础');
const proQ = data.filter(q => q.bigSubject === '专业基础');
console.log(`公共基础: ${pubQ.length} 题`);
console.log(`专业基础: ${proQ.length} 题`);
const years = [...new Set(data.map(q => q.year))].sort();
console.log(`年份范围: ${years.join(', ')}`);
const smalls = [...new Set(data.map(q => q.smallSubject))];
console.log(`小科目数: ${smalls.length}`);
console.log(`含图片的题目: ${data.filter(q => /<img/.test([q.question, q.A, q.B, q.C, q.D, q.analysis].join(''))).length} 题`);
console.log(`含公式的题目: ${data.filter(q => /\$[^$]+\$/.test([q.question, q.A, q.B, q.C, q.D, q.analysis].join(''))).length} 题`);
