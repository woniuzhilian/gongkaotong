const fs=require('fs');const d=JSON.parse(fs.readFileSync('exam-quiz/src/data/questions.json','utf8'))
console.log('keys:',Object.keys(d[0]).join(','))
const FIELDS=['question','A','B','C','D','analysis']
const cats={},years={},fcount={}
for(const q of d){cats[q.category]=(cats[q.category]||0)+1}
console.log('categories:',JSON.stringify(cats))
for(const q of d){years[q.year]=(years[q.year]||0)+1}
console.log('years:',JSON.stringify(years))
