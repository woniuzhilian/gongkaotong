const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const DB = path.join(ROOT, 'exam-quiz', 'src', 'data', 'questions.json');
const IMG_DIR = path.join(ROOT, 'exam-quiz', 'public', 'images');
const raw = fs.readFileSync(DB, 'utf8');
const data = JSON.parse(raw);

const FIELDS = ['question', 'A', 'B', 'C', 'D', 'analysis'];
const existingImages = new Set(fs.readdirSync(IMG_DIR));
const label = (q) => `[${q.bigSubject} ${q.year}-${q.yearQnum} id=${q.id}]`;

const issues = [];
const add = (type, q, msg) => issues.push([type, label(q), msg]);

/* ---------- A. 真实乱码：不可见/异常码点（用转义，不用字面量） ---------- */
const BAD_CODEPOINTS = {
  'U+FFFD 替换符': 0xfffd,
  'U+0000-NUL': 0x00,
  'U+25A1 空心方框□': 0x25a1,
  'U+FFFC 对象替换符': 0xfffc,
  'U+FFFE': 0xfffe,
};
const brokenCounts = {};
for (const q of data) {
  for (const f of FIELDS) {
    const t = q[f] || '';
    for (const ch of t) {
      const cp = ch.codePointAt(0);
      for (const [name, v] of Object.entries(BAD_CODEPOINTS)) {
        if (cp === v) {
          brokenCounts[name] = (brokenCounts[name] || 0) + 1;
          add('BROKEN_CHAR', q, `${f}: ${name}`);
        }
      }
      // 控制字符（除 TAB LF CR）
      if (cp < 0x20 && cp !== 0x09 && cp !== 0x0a && cp !== 0x0d) {
        brokenCounts['其他控制字符'] = (brokenCounts['其他控制字符'] || 0) + 1;
      }
      // 私用区
      if (cp >= 0xe000 && cp <= 0xf8ff) {
        brokenCounts['私用区字符(PUA,常见于PDF数学字体)'] = (brokenCounts['私用区字符(PUA,常见于PDF数学字体)'] || 0) + 1;
        add('PUA_CHAR', q, `${f}: U+${cp.toString(16).toUpperCase()}`);
      }
    }
  }
}
console.log('=== A. 异常字符统计 ===');
console.log(Object.keys(brokenCounts).length ? brokenCounts : '无');

/* ---------- B. 图片引用 ---------- */
let imgTotal = 0; const missingImg = [];
for (const q of data) {
  for (const f of FIELDS) {
    const t = q[f] || '';
    for (const m of t.matchAll(/<img[^>]*?src\s*=\s*["']([^"']+)["']/gi)) {
      imgTotal++;
      const fname = m[1].split('/').pop();
      if (!existingImages.has(fname)) missingImg.push([label(q), f, m[1]]);
    }
  }
}
console.log('\n=== B. 图片引用 ===');
console.log(`img标签总数: ${imgTotal}, 缺失: ${missingImg.length}`);
for (const x of missingImg) console.log('  ', x.join(' | '));

/* ---------- C. 提到"如图"但无配图 ---------- */
const noImgButRef = [];
for (const q of data) {
  const all = FIELDS.map(f => q[f] || '').join(' ');
  const hasImg = /<img/i.test(all);
  if (!hasImg && /如图所示|如下图|见下图|如图|题图/.test(q.question || '')) {
    noImgButRef.push([label(q), (q.question || '').slice(0, 60)]);
  }
}
console.log('\n=== C. 题干提及图但整题无配图 ===', noImgButRef.length);
for (const x of noImgButRef) console.log('  ', x.join(' | '));

/* ---------- D. 空公式 ---------- */
const emptyF = [];
for (const q of data) {
  for (const f of FIELDS) {
    const t = q[f] || '';
    const m = t.match(/\$\s*\$/g);
    if (m) emptyF.push([label(q), f, m.length, t.slice(0, 100)]);
  }
}
console.log('\n=== D. 空公式 $<空白>$ ===', emptyF.length, '处');
for (const x of emptyF.slice(0, 15)) console.log('  ', x.join(' | '));

/* ---------- E. $ 号未闭合 ---------- */
const oddDollar = [];
for (const q of data) {
  for (const f of FIELDS) {
    const t = q[f] || '';
    const cnt = (t.match(/\$/g) || []).length;
    if (cnt % 2 !== 0) oddDollar.push([label(q), f, cnt, t.slice(0, 120)]);
  }
}
console.log('\n=== E. $号奇数(公式未闭合) ===', oddDollar.length, '处');
for (const x of oddDollar.slice(0, 15)) console.log('  ', x.join(' | '));

/* ---------- F. 选项重复 ---------- */
const dupOpt = [];
for (const q of data) {
  const o = ['A', 'B', 'C', 'D'].map(k => (q[k] || '').trim());
  for (let i = 0; i < 4; i++) for (let j = i + 1; j < 4; j++) {
    if (o[i] && o[i] === o[j]) dupOpt.push([label(q), `${'ABCD'[i]}=${'ABCD'[j]}`, o[i].slice(0, 50)]);
  }
}
console.log('\n=== F. 选项内容完全相同 ===', dupOpt.length, '处');
for (const x of dupOpt.slice(0, 15)) console.log('  ', x.join(' | '));

/* ---------- G. 空字段 ---------- */
const emptyField = [];
for (const q of data) {
  for (const f of ['question', 'A', 'B', 'C', 'D', 'answer', 'analysis']) {
    if (typeof q[f] === 'string' && q[f].trim() === '') emptyField.push([label(q), f]);
  }
}
console.log('\n=== G. 字段为空 ===', emptyField.length, '处');
const gf = {}; for (const [, f] of emptyField) gf[f] = (gf[f] || 0) + 1;
console.log('  按字段:', gf);

/* ---------- H. 答案格式 ---------- */
const badAns = [];
for (const q of data) {
  const a = (q.answer || '').trim();
  if (!/^[A-D]+$/.test(a)) badAns.push([label(q), JSON.stringify(a)]);
}
console.log('\n=== H. 答案非A-D格式 ===', badAns.length);
for (const x of badAns.slice(0, 15)) console.log('  ', x.join(' | '));

/* ---------- I. HTML 标签 ---------- */
const htmlBad = [];
for (const q of data) {
  for (const f of FIELDS) {
    const t = q[f] || '';
    for (const tag of ['table', 'tr', 'td', 'th', 'b', 'i', 'span', 'sub', 'sup']) {
      const o = (t.match(new RegExp(`<${tag}[\\s>/]`, 'g')) || []).length;
      const c = (t.match(new RegExp(`</${tag}>`, 'g')) || []).length;
      if (o !== c) htmlBad.push([label(q), f, tag, o, c]);
    }
  }
}
console.log('\n=== I. HTML标签开闭不匹配 ===', htmlBad.length);
for (const x of htmlBad.slice(0, 15)) console.log('  ', x.join(' | '));

/* ---------- J. id / (bigSubject,year,yearQnum) 重复 ---------- */
const idC = {}, keyC = {};
for (const q of data) {
  idC[q.id] = (idC[q.id] || 0) + 1;
  const k = `${q.bigSubject}|${q.year}|${q.yearQnum}`;
  (keyC[k] = keyC[k] || []).push(q.id);
}
const dupId = Object.entries(idC).filter(([, c]) => c > 1);
const dupKey = Object.entries(keyC).filter(([, v]) => v.length > 1);
console.log('\n=== J. 重复 ===');
console.log('  id重复:', dupId.length, dupId.slice(0, 10));
console.log('  (大科目,年份,年内题号)重复:', dupKey.length);
for (const [k, v] of dupKey.slice(0, 10)) console.log(`   ${k} -> ids ${v.join(',')}`);

/* ---------- K. LaTeX 命令合法性 ---------- */
const knownCmd = new Set(('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi pi rho sigma tau upsilon phi chi psi omega' +
  'Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega' +
  'times div cdot pm mp leq geq neq approx equiv sim cong propto in notin subset supsetsubseteq supseteq cup cap emptyset varnothing' +
  'rightarrow leftarrow Rightarrow Leftarrow leftrightarrow Leftrightarrow mapsto to gets' +
  'infty partial nabla forall exists neg land lor vee wedge oplus otimes perp parallel angle triangle square circ bullet star' +
  'ldots cdots vdots ddots dots' +
  'frac dfrac tfrac sqrt binom choose' +
  'sum prod int iint iiint oint lim max min sup inf varlim' +
  'hat bar tilde vec dot dcheck widehat widetilde overline underline over underline' +
  'left right big Big bigg Bigg langle ranglelangle' +
  'text mathrm mathbf mathit mathcal mathbb mathsf operatorname' +
  'begin end array matrix pmatrix bmatrix vmatrix Vmatrix cases aligned gather equation' +
  'sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh log ln lg exp' +
  'degree prime circ ! ? , ; : quad qquad spacespace' +
  'Bigg lbrace rbrace lbrack rbrack vert Vert| |langle|rangle').split(/\s+/));
const unknownCmd = {};
const unknownSamples = [];
for (const q of data) {
  for (const f of FIELDS) {
    const t = q[f] || '';
    for (const m of t.matchAll(/\$([^$]+)\$/g)) {
      for (const c of m[1].matchAll(/\\([a-zA-Z]+)/g)) {
        if (!knownCmd.has(c[1])) {
          unknownCmd[c[1]] = (unknownCmd[c[1]] || 0) + 1;
          if (unknownCmd[c[1]] <= 2) unknownSamples.push([label(q), f, '\\' + c[1], m[1].slice(0, 60)]);
        }
      }
    }
  }
}
console.log('\n=== K. 公式中非常见 LaTeX 命令 ===');
console.log(Object.entries(unknownCmd).sort((a, b) => b[1] - a[1]).slice(0, 40).map(([k, v]) => `\\${k}:${v}`).join('  '));
console.log('  样例:');
for (const x of unknownSamples.slice(0, 20)) console.log('   ', x.join(' | '));

/* ---------- L. 纯文本上下标（真问题：如 x2 应为 x^2） ---------- */
const subSup = [];
for (const q of data) {
  for (const f of FIELDS) {
    let t = q[f] || '';
    t = t.replace(/<[^>]+>/g, ' ');
    // 剔除公式、数字串、年份
    const pure = t.replace(/\$[^$]*\$/g, ' ');
    for (const m of pure.matchAll(/[a-zA-Zα-ωΑ-Ω](?=[0-9])/g)) {
      const ctx = pure.slice(Math.max(0, m.index - 12), m.index + 8);
      if (/^\d{4}$/.test(ctx.trim())) continue;
      subSup.push([label(q), f, ctx.replace(/\s+/g, ' ').trim()]);
    }
  }
}
console.log('\n=== L. 纯文本中"字母紧跟数字"(疑似上下标丢失) ===', subSup.length, '处');
for (const x of subSup.slice(0, 25)) console.log('  ', x.join(' | '));

/* ---------- M. 明显截断/错乱的极限表达式 ---------- */
const brokenLim = [];
for (const q of data) {
  for (const f of FIELDS) {
    const t = q[f] || '';
    if (/lim\s*[a-zA-Z0-9]/.test(t.replace(/\$[^$]*\$/g, '')) || /x\\rightarrow|\\rightarrow1|\\rightarrow\d/.test(t)) {
      brokenLim.push([label(q), f, t.slice(0, 90)]);
    }
  }
}
console.log('\n=== M. 疑似极限/公式塌陷(纯文本 lim 或 \rightarrow 紧跟数字) ===', brokenLim.length, '处');
for (const x of brokenLim.slice(0, 12)) console.log('  ', x.join(' | '));

/* ---------- 汇总 ---------- */
const byType = {};
for (const [t] of issues) byType[t] = (byType[t] || 0) + 1;
console.log('\n=== 结构性错误汇总(需人工核对PDF) ===', byType);
console.log(`总题数 ${data.length}`);
