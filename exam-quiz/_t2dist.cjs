const fs=require('fs');const d=JSON.parse(fs.readFileSync('exam-quiz/src/data/questions.json','utf8'))
const FIELDS=['question','A','B','C','D','analysis']
const CMDS=new Set(('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi pi rho sigma tau upsilon phi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Phi Psi Omega varepsilon varsigma varphi vartheta sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh log ln lg exp lim max min det int sum prod oint iint iiint sqrt frac dfrac tfrac binom leq geq neq approx infty cdots ldots dots rightarrow leftarrow Rightarrow Leftarrow Leftrightarrow to mapsto sim simeq equiv partial nabla in notin subset supset cup cap emptyset forall exists mathrm mathbf mathbb mathcal mathit text mbox operatorname begin end cases matrix pmatrix left right big Big bigg Bigg overline underline hat bar vec dot ddot tilde widetilde widehat circ odot oplus otimes lbrace rbrace neq Theta theta').split(' '))
function mask(f){let s=f.replace(/\[a-zA-Z]+/g,m=>'#'.repeat(m.length));s=s.replace(/[_^]\{[^{}]*\}/g,m=>'#'.repeat(m.length));s=s.replace(/[_^][A-Za-z0-9]/g,'##');return s}
function hits(f){const s=mask(f);const o=[];const re=/([A-Za-z])(\d{1,2})(?![\dA-Za-z])/g;let m;while((m=re.exec(s)))o.push({i:m.index,d:m[2]});return o}
const rows=[]
for(const q of d){let n=0;const fs2=new Set()
 for(const f of FIELDS){const t=q[f]||'';for(const m of t.matchAll(/\$([^$]+)\$/g))if(hits(m[1]).length){n++;fs2.add(f)}}
 if(n)rows.push({id:q.id,big:q.bigSubject,small:q.smallSubject,y:q.year,yn:q.yearQnum,n,fields:[...fs2].join(',')})}
const big={},byField={},ys={}
for(const r of rows){big[r.big]=(big[r.big]||0)+1;ys[r.y]=(ys[r.y]||0)+1;for(const f of r.fields.split(','))byField[f]=(byField[f]||0)+1}
console.log('T2真命中题数',rows.length);console.log('big:',JSON.stringify(big));console.log('year:',JSON.stringify(ys));console.log('fields:',JSON.stringify(byField))
console.log('总命中片段',rows.reduce((a,r)=>a+r.n,0))
