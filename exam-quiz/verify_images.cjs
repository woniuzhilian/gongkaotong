const fs = require('fs');
const path = require('path');
const ROOT = __dirname;
const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'exam-quiz/src/data/questions.json'), 'utf8'));
const IMG_ROOT = path.join(ROOT, 'exam-quiz', 'public');

function walk(dir, base) {
  let out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    const b = base ? base + '/' + e.name : e.name;
    if (e.isDirectory()) out = out.concat(walk(p, b));
    else out.push(b);
  }
  return out;
}
const all = walk(path.join(IMG_ROOT, 'images'), 'images');
const set = new Set(all);
console.log('public/images 下图片总数(递归):', all.length);

const FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis'];
const SRC_RE = new RegExp('src\\s*=\\s*"([^"]+)"', 'g');
const missing = [];
let totalRefs = 0;
for (const q of data) {
  for (const f of FIELDS) {
    const t = q[f] || '';
    let m;
    SRC_RE.lastIndex = 0;
    while ((m = SRC_RE.exec(t)) !== null) {
      totalRefs++;
      const rel = m[1].replace(/^\/+/, '');
      if (!set.has(rel)) missing.push('id=' + q.id + ' [' + q.bigSubject + ' ' + q.year + '-' + q.yearQnum + '] ' + f + ' -> ' + m[1]);
    }
  }
}
console.log('img引用总数: ' + totalRefs + ', 真实缺失: ' + missing.length);
for (const x of missing) console.log('  ' + x);

console.log('\n=== 仅有A选项的题目 ===');
for (const q of data) {
  if ((q.B || '').trim() === '' && (q.C || '').trim() === '' && (q.D || '').trim() === '') {
    console.log('id=' + q.id + ' [' + q.bigSubject + ' ' + q.year + '-' + q.yearQnum + '] ' + q.smallSubject + ' | 答案=' + q.answer + ' | ' + (q.question || '').slice(0, 70));
  }
}

const dist = {};
for (const q of data) {
  const n = ['A', 'B', 'C', 'D'].filter((k) => (q[k] || '').trim() !== '').length;
  dist[n] = (dist[n] || 0) + 1;
}
console.log('\n选项数量分布:', dist);
