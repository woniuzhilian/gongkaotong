const fs=require('fs');const d=JSON.parse(fs.readFileSync('exam-quiz/src/data/questions.json','utf8'))
const FIELDS=['question','A','B','C','D','analysis']
function maskA(f){let s=f.replace(/\[a-zA-Z]+/g,m=>'#'.repeat(m.length));s=s.replace(/[_^]\{[^{}]*\}/g,m=>'#'.repeat(m.length));s=s.replace(/[_^][A-Za-z0-9]/g,'##');return s}
function maskB(f){let s=f.replace(/\[a-zA-Z]+/g,m=>m.length?'#'.repeat(m.length):m);s=s.replace(/[_^]\{[^{}]*\}/g,m=>'#'.repeat(m.length));s=s.replace(/[_^][A-Za-z0-9]/g,'##');return s}
function count(mask,re){let q=0,fr=0,hi=0
 for(const x of d){let hit=false;for(const f of FIELDS){const t=x[f]||'';for(const m of t.matchAll(/\$([^$]+)\$/g)){const s=mask(m[1]);const n=[...s.matchAll(re)].length;if(n){fr++;hi+=n;hit=true}}}if(hit)q++}
 return{q,fr,hi}}
console.log('A 1-2位,不排除点 :',JSON.stringify(count(maskA,/([A-Za-z])(\d{1,2})(?![\dA-Za-z])/g)))
console.log('B 1位,排除点号   :',JSON.stringify(count(maskB,/([A-Za-z])(\d)(?![\dA-Za-z.])/g)))
console.log('C 1-2位,不排除点 :',JSON.stringify(count(maskB,/([A-Za-z])(\d{1,2})(?![\dA-Za-z])/g)))
