const fs=require('fs');
const qs=JSON.parse(fs.readFileSync('exam-quiz/src/data/questions.json','utf8'));
const ids=[8,12,17,61,131,136,167,207,253,256,267,318,326,371,376,380,383,413,492,501,521,615,617,623,684,731,735,737,855,856,863,971,973,976,1020,1095,1103,1122,1140,1214,1217,1280,1294,1336,1372,1375,1380,1410];
const D='$';
let out='';
for(const id of ids){
  const q=qs.find(x=>x.id===id);
  out+='===== id='+id+' ['+q.bigSubject+' '+q.year+'-'+q.yearQnum+'] '+q.smallSubject+'\n';
  for(const f of ['question','A','B','C','D']){
    out+='  '+f+': '+String(q[f]||'').replace(/\n/g,' / ')+'\n';
  }
}
fs.writeFileSync('_t1_current.txt',out,'utf8');
console.log('ids='+ids.length+' bytes='+out.length);
