// 题库数据处理工具 - 筛选、统计、分组

import questionsData from '../data/questions.json'

// 获取全部题目
export function getAllQuestions() {
  return questionsData
}

// 按大科目筛选
export function getQuestionsByBigSubject(bigSubject) {
  return questionsData.filter(q => q.bigSubject === bigSubject)
}

// 获取某大科目下的所有小科目列表（按出现顺序）
export function getSmallSubjects(bigSubject) {
  const questions = getQuestionsByBigSubject(bigSubject)
  const seen = new Set()
  const result = []
  for (const q of questions) {
    if (!seen.has(q.smallSubject)) {
      seen.add(q.smallSubject)
      result.push({
        name: q.smallSubject,
        count: questions.filter(x => x.smallSubject === q.smallSubject).length
      })
    }
  }
  return result
}

// 获取某大科目下的所有年份列表（按出现顺序）
export function getYears(bigSubject) {
  const questions = getQuestionsByBigSubject(bigSubject)
  const seen = new Set()
  const result = []
  for (const q of questions) {
    if (!seen.has(q.year)) {
      seen.add(q.year)
      result.push({
        year: q.year,
        count: questions.filter(x => x.year === q.year).length
      })
    }
  }
  return result
}

// 按小科目获取题目（按年份+题号升序，补考年份紧随正考之后）
export function getQuestionsBySmallSubject(bigSubject, smallSubject) {
  const list = getQuestionsByBigSubject(bigSubject).filter(q => q.smallSubject === smallSubject)
  return list.slice().sort((a, b) => {
    const ay = parseInt(a.year, 10)
    const by = parseInt(b.year, 10)
    if (ay !== by) return ay - by
    const ab = a.year.includes('补') ? 1 : 0
    const bb = b.year.includes('补') ? 1 : 0
    if (ab !== bb) return ab - bb
    return (a.yearQnum || 0) - (b.yearQnum || 0)
  })
}

// 按年份获取题目（保持原顺序）
export function getQuestionsByYear(bigSubject, year) {
  return getQuestionsByBigSubject(bigSubject).filter(q => q.year === year)
}

// 按id列表获取题目（用于错题本）
export function getQuestionsByIds(bigSubject, ids) {
  return getQuestionsByBigSubject(bigSubject).filter(q => ids.includes(q.id))
}

// 计算正确率
export function calcCorrectRate(questions, userAnswers) {
  let correct = 0
  let answered = 0
  for (const q of questions) {
    const userAns = userAnswers[q.id]
    if (userAns) {
      answered++
      if (userAns === q.answer) {
        correct++
      }
    }
  }
  return {
    total: questions.length,
    answered,
    correct,
    wrong: answered - correct,
    rate: answered > 0 ? Math.round((correct / answered) * 100) : 0
  }
}

// 生成sectionKey（用于存储答题记录的key）
export function makeSectionKey(mode, sectionValue) {
  if (mode === 'smallSubject') {
    return `sub_${sectionValue}`
  } else if (mode === 'year') {
    return `year_${sectionValue}`
  } else if (mode === 'wrong') {
    return `wrong_${sectionValue}`
  }
  return sectionValue
}
