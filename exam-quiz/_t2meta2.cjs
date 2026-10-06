const fs=require('fs');const d=JSON.parse(fs.readFileSync('exam-quiz/src/data/questions.json','utf8'))
const big={},sm={}
for(const q of d){big[q.bigSubject]=(big[q.bigSubject]||0)+1;sm[q.smallSubject]=(sm[q.smallSubject]||0)+1}
console.log('big:',JSON.stringify(big));console.log('small:',JSON.stringify(sm))
