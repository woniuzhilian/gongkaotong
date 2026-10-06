const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const DB = path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json');
const raw = fs.readFileSync(DB, 'utf8');
const qs = JSON.parse(raw);

function fields(q) {
  return [['question', q.question], ['A', q.A], ['B', q.B], ['C', q.C], ['D', q.D], ['analysis', q.analysis]];
}

// ---- 1. U+FFFD ----
const re = /\uFFFD/g;
let total = 0;
const affected = [];
for (const q of qs) {
  let c = 0;
  for (const [k, v] of fields(q)) c += ((v || '').match(re) || []).length;
  if (c) { total += c; affected.push({ id: q.id, big: q.bigSubject, year: q.year, yq: q.yearQnum, small: q.smallSubject, count: c }); }
}
console.log('=== 1. U+FFFD 乱码 ===');
console.log('原始文件字节级总数:', (raw.match(re) || []).length);
console.log('解析后字段级总数:', total, '影响题目数:', affected.length);
console.log('按大科目:', affected.reduce((a, x) => ((a[x.big] = (a[x.big] || 0) + x.count), a), {}));

// 上下文取样
console.log('\n--- 前 15 处上下文 ---');
let shown = 0;
for (const q of qs) {
  for (const [k, v] of fields(q)) {
    if (!v || !v.includes('\uFFFD')) continue;
    const idx = v.indexOf('\uFFFD');
    const ctx = v.slice(Math.max(0, idx - 30), idx + 30).replace(/\uFFFD/g, '<U+FFFD>');
    console.log(`id=${q.id} [${k}] ...${ctx}...`);
    if (++shown >= 15) break;
  }
  if (shown >= 15) break;
}

// 乱码字符前后字符的码点分布，判断是哪种丢失
const codes = {};
for (const q of qs) {
  for (const [, v] of fields(q)) {
    if (!v) continue;
    for (let i = 0; i < v.length; i++) {
      if (v[i] === '\uFFFD') {
        const next = v[i + 1];
        const key = next ? 'U+' + next.codePointAt(0).toString(16).toUpperCase() : 'END';
        codes[key] = (codes[key] || 0) + 1;
      }
    }
  }
}
const top = Object.entries(codes).sort((a, b) => b[1] - a[1]).slice(0, 15);
console.log('\n--- 乱码后续字符码点 TOP15 (推测被替换的原字符) ---');
console.log(top.map(([k, v]) => `${k}:${v}`).join('  '));

// 是否存在连续乱码块
let runs = {};
for (const q of qs) {
  for (const [, v] of fields(q)) {
    if (!v) continue;
    for (const m of v.match(/\uFFFD+/g) || []) runs[m.length] = (runs[m.length] || 0) + 1;
  }
}
console.log('\n--- 连续乱码长度分布 (长度:出现组数) ---');
console.log(Object.entries(runs).sort((a, b) => a[0] - b[0]).map(([k, v]) => `${k}:${v}`).join('  '));
