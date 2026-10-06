const fs=require('fs')
const FIELDS=['question','A','B','C','D','analysis']
const a=JSON.parse(fs.readFileSync('_fix_backup/questions_BEFORE_T6B.json','utf8'))
const b=JSON.parse(fs.readFileSync('exam-quiz/src/data/questions.json','utf8'))
let n=0,keys=new Set()
if(a.length!==b.length) console.log('LEN DIFF', a.length, b.length)
for(let i=0;i<a.length;i++){
  const ka=Object.keys(a[i]).sort().join(','), kb=Object.keys(b[i]).sort().join(',')
  if(ka!==kb) console.log('KEYSET id='+a[i].id)
  for(const k of Object.keys(a[i])){
    if(a[i][k]!==b[i][k]){ if(!FIELDS.includes(k)) console.log('NON-TEXT KEY CHANGED id='+a[i].id+' '+k); n++; keys.add(a[i].id+':'+k) }
  }
}
console.log('changed='+n+' ids='+[...keys].join(' '))
