const fs=require('fs');const path=require('path')
const d=JSON.parse(fs.readFileSync('exam-quiz/src/data/questions.json','utf8'))
const q=d.find(x=>x.id===24)
const q2=d.find(x=>x.id===6)
for(const x of [q,q2]){console.log('id='+x.id+' analysis='+JSON.stringify((x.analysis||'').slice(0,120)))}
// 直接调用 t2_scan 的 mask/hits 逻辑副本
const CMDS=new Set(('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi pi rho sigma tau upsilon phi chi psi omega').split(' '))
function maskScan(frag){let s=frag.replace(/\[a-zA-Z]+/g,m=>(CMDS.has(m.slice(1))||/^[a-zA-Z]+$/.test(m.slice(1)))?'#'.repeat(m.length):m);s=s.replace(/[_^]\{[^{}]*\}/g,m=>'#'.repeat(m.length));s=s.replace(/[_^][A-Za-z0-9]/g,'##');return s}
function maskAll(f){let s=f.replace(/\[a-zA-Z]+/g,m=>'#'.repeat(m.length));s=s.replace(/[_^]\{[^{}]*\}/g,m=>'#'.repeat(m.length));s=s.replace(/[_^][A-Za-z0-9]/g,'##');return s}
const re=/([A-Za-z])(\d{1,2})(?![\dA-Za-z])/g
for(const m of q.analysis.matchAll(/\$([^$]+)\$/g)){
  console.log('frag='+JSON.stringify(m[1]).slice(0,80),'scan='+JSON.stringify(maskScan(m[1]).match(new RegExp(re.source,'g'))),'all='+JSON.stringify(maskAll(m[1]).match(new RegExp(re.source,'g'))))
}
