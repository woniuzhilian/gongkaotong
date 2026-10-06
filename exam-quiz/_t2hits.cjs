const fs=require('fs');const CMDS=new Set(('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi pi rho sigma tau upsilon phi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Phi Psi Omega varepsilon varsigma varphi vartheta sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh log ln lg exp lim max min det int sum prod oint iint iiint sqrt frac dfrac tfrac binom leq geq neq approx infty cdots ldots dots rightarrow leftarrow Rightarrow Leftarrow Leftrightarrow to mapsto sim simeq equiv partial nabla in notin subset supset cup cap emptyset forall exists mathrm mathbf mathbb mathcal mathit text mbox operatorname begin end cases matrix pmatrix left right big Big bigg Bigg overline underline hat bar vec dot ddot tilde widetilde widehat circ odot oplus otimes lbrace rbrace neq Theta theta').split(' '));
// 掩码：\command 与 _{..} ^{..} _d ^d 用等长 # 替换，其余原样 => 位置不变
function mask(frag) {
  let s = frag.replace(/\\[a-zA-Z]+/g, m => (CMDS.has(m.slice(1)) || /^[a-zA-Z]+$/.test(m.slice(1)))
    ? '#'.repeat(m.length) : m)
  s = s.replace(/[_^]\{[^{}]*\}/g, m => '#'.repeat(m.length))
  s = s.replace(/[_^][A-Za-z0-9]/g, '##')
  return s
}

// 命中：字母紧跟数字；数字可 1~2 位
function hits(frag) {
  const s = mask(frag)
  const out = []
  const re = /([A-Za-z])(\d{1,2})(?![\dA-Za-z])/g
  let m
  while ((m = re.exec(s))) {
    const i = m.index
    out.push({
      i,
      letter: m[1],
      digits: m[2],
      // 原文上下文(用原始 frag 切片，位置一一对应)
      ctx: frag.slice(Math.max(0, i - 10), i + 1 + m[2].length + 10),
      // 字母前一个字符：判断是否 \command 尾部或另一字母
      prev: i > 0 ? frag[i - 1] : '',
      // 数字后面
      next: frag.slice(i + 1 + m[2].length, i + 1 + m[2].length + 1)
    })
  }
  return out
}

const NUMISH = new Set('0123456789')
function bucket(frag, h) {
  const c = h.ctx
  if (/\\cdots\s*[\^_{]/.test(c) || /\\cdots\^/.test(c)) return 'B-cdots当乘号'
  if (/[-−;]\s*$/.test(c.slice(0, 11)) && /^[12]/.test(h.digits)) return 'A-负指数丢失(^{1}应为^{-1})'
  if (h.digits.length === 1 && /[A-Za-z]$/.test(c.slice(0, 11)) === false) {
    // 单位类：字母是 m/g/s/J/K/P 等且紧跟 ^{n} 形式已丢
    if (/[{]\^?\d*[}]|\\mathrm/.test(c)) return 'D-单位或mathrm内数字'
  }
  if (/^\\pm|^\\times|^\\cdot/.test(c) ) return 'Z-命令尾误命中'
  return 'E-其它待判'
}


module.exports={mask,hits}
