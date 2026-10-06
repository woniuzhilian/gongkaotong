const fs=require('fs');
const qs=JSON.parse(fs.readFileSync('exam-quiz/src/data/questions.json','utf8'));
for(const q of qs){
  if(q.year==='2017' && +q.yearQnum>=52 && +q.yearQnum<=58){
    console.log('id='+q.id+' '+q.year+'-'+q.yearQnum+' ['+q.smallSubject+'] :: '+String(q.question).slice(0,60).replace(/\n/g,' '));
  }
}
