const fs=require('fs')
const data=JSON.parse(fs.readFileSync('exam-quiz/src/data/questions.json','utf8'))
const FIELDS=['question','A','B','C','D','analysis']
function maskScanLike(frag){let s=frag.replace(/\[a-zA-Z]+/g,m=>'#'.repeat(m.length));s=s.replace(/[_^]\{[^{}]*\}/g,m=>'#'.repeat(m.length));s=s.replace(/[_^][A-Za-z0-9]/g,'##');return s}
function setOf(fn){const S=new Set()
 for(const q of data){for(const f of FIELDS){const t=q[f]||'';for(const m of t.matchAll(/\$([^$]+)\$/g)){const s=fn(m[1]);if(new RegExp('([A-Za-z])(\\d{1,2})(?![\\dA-Za-z])','g').test(s)){S.add(q.id);break}}}}
 return S}
const A=setOf(maskScanLike)
// 现在用 require 引入 t2_scan 的 hits(通过复制文件已验证=102),改为直接调用其源码
const src=fs.readFileSync('exam-quiz/t2_scan.cjs','utf8')
const body=src.slice(src.indexOf('// 掩码'),src.indexOf('const rows = []'))
const sandbox=src.slice(0,src.indexOf('const DB'))+'\n'+body
fs.writeFileSync('_t2hits.cjs',"const fs=require('fs');const CMDS=new Set(('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi pi rho sigma tau upsilon phi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Phi Psi Omega varepsilon varsigma varphi vartheta sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh log ln lg exp lim max min det int sum prod oint iint iiint sqrt frac dfrac tfrac binom leq geq neq approx infty cdots ldots dots rightarrow leftarrow Rightarrow Leftarrow Leftrightarrow to mapsto sim simeq equiv partial nabla in notin subset supset cup cap emptyset forall exists mathrm mathbf mathbb mathcal mathit text mbox operatorname begin end cases matrix pmatrix left right big Big bigg Bigg overline underline hat bar vec dot ddot tilde widetilde widehat circ odot oplus otimes lbrace rbrace neq Theta theta').split(' '));\n"+body+"\nmodule.exports={mask,hits}\n")
const {mask,hits}=require('./_t2hits.cjs')
const B=new Set();for(const q of data){for(const f of FIELDS){const t=q[f]||'';for(const m of t.matchAll(/\$([^$]+)\$/g)){if(hits(m[1]).length){B.add(q.id);break}}}}
console.log('A(直接实现)='+A.size+'  B(hits实现)='+B.size)
const onlyA=[...A].filter(x=>!B.has(x)).slice(0,6)
console.log('只在A里:',JSON.stringify(onlyA))
for(const id of onlyA){const q=data.find(x=>x.id===id);for(const f of FIELDS){const t=q[f]||'';for(const m of t.matchAll(/\$([^$]+)\$/g)){if(new RegExp('([A-Za-z])(\\d{1,2})(?![\\dA-Za-z])','g').test(maskScanLike(m[1])))console.log('  id='+id+' '+f+' frag='+JSON.stringify(m[1]).slice(0,90)+'  maskB='+JSON.stringify(mask(m[1])).slice(0,90))}}}
