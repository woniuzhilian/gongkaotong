const fs=require('fs')
const data=JSON.parse(fs.readFileSync('exam-quiz/src/data/questions.json','utf8'))
const {mask,hits}=require('./_t2hits.cjs')
function maskAllCommands(f){let s=f.replace(/\[a-zA-Z]+/g,m=>'#'.repeat(m.length));s=s.replace(/[_^]\{[^{}]*\}/g,m=>'#'.repeat(m.length));s=s.replace(/[_^][A-Za-z0-9]/g,'##');return s}
const RE=/([A-Za-z])(\d{1,2})(?![\dA-Za-z])/g
const FIELDS=['question','A','B','C','D','analysis']
let n=0
for(const q of data){
  for(const f of FIELDS){
    const t=q[f]||''
    for(const m of t.matchAll(/\$([^$]+)\$/g)){
      const a=new RegExp(RE.source,'g').test(maskAllCommands(m[1]))
      const b=hits(m[1]).length>0
      if(a!==b&&n++<5){
        console.log('id='+q.id+' '+f)
        console.log('  frag='+JSON.stringify(m[1]))
        console.log('  maskAll='+JSON.stringify(maskAllCommands(m[1])))
        console.log('  maskHits='+JSON.stringify(mask(m[1])))
      }
    }
  }
}
console.log('disagree='+n)
