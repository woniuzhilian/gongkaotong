// localStorage 封装 - 刷题进度、答题记录、错题本持久化存储
// 所有写操作会自动防抖同步到 Supabase 云端

import { scheduleCloudSync, pullFromCloud } from './supabase'

const STORAGE_KEYS = {
  PROGRESS: 'exam_quiz_progress',      // 各板块进度map + lastActive
  ANSWERS: 'exam_quiz_answers',        // 答题记录
  WRONG: 'exam_quiz_wrong',            // 错题本
  RESULTS: 'exam_quiz_results',        // 各板块最近一次完成结果（正确率）
  SETTINGS: 'exam_quiz_settings'       // 设置
}

// 通用读取
function get(key, defaultValue = null) {
  try {
    const val = localStorage.getItem(key)
    return val ? JSON.parse(val) : defaultValue
  } catch (e) {
    return defaultValue
  }
}

// 通用写入
function set(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
    return true
  } catch (e) {
    return false
  }
}

// 收集当前 4 份业务数据，通知云端同步（防抖）
function notifyCloudSync() {
  const localData = {
    progress: get(STORAGE_KEYS.PROGRESS, {}),
    answers: get(STORAGE_KEYS.ANSWERS, {}),
    wrong: get(STORAGE_KEYS.WRONG, {}),
    results: get(STORAGE_KEYS.RESULTS, {})
  }
  scheduleCloudSync(localData)
}

// 生成板块唯一key
function makeProgressKey(bigSubject, mode, section) {
  return `${bigSubject}__${mode}__${section}`
}

// ===== 刷题进度 =====
// 结构：{ lastActive: {bigSubject,mode,section,currentIndex}, sections: { "key": {bigSubject,mode,section,currentIndex} } }
function getProgressStore() {
  const raw = get(STORAGE_KEYS.PROGRESS, null)
  // 兼容旧格式：直接是 {bigSubject, mode, section, currentIndex}
  if (raw && raw.bigSubject && raw.mode && raw.section !== undefined) {
    const key = makeProgressKey(raw.bigSubject, raw.mode, raw.section)
    return {
      lastActive: { ...raw },
      sections: { [key]: { ...raw } }
    }
  }
  // 新格式
  if (raw && raw.sections) return raw
  return { lastActive: null, sections: {} }
}

// 获取最近一次刷题进度（用于首页恢复提示）
export function getProgress() {
  const store = getProgressStore()
  return store.lastActive
}

// 获取指定板块的进度
export function getSectionProgress(bigSubject, mode, section) {
  const store = getProgressStore()
  const key = makeProgressKey(bigSubject, mode, section)
  return store.sections[key] || null
}

// 保存进度（同时更新板块进度和最近活跃）
export function setProgress(progress) {
  const store = getProgressStore()
  const key = makeProgressKey(progress.bigSubject, progress.mode, progress.section)
  store.sections[key] = { ...progress }
  store.lastActive = { ...progress }
  const ok = set(STORAGE_KEYS.PROGRESS, store)
  notifyCloudSync()
  return ok
}

// 清除最近活跃进度（完成板块后调用，不清除各板块独立进度）
export function clearProgress() {
  const store = getProgressStore()
  store.lastActive = null
  const ok = set(STORAGE_KEYS.PROGRESS, store)
  notifyCloudSync()
  return ok
}

// 清除指定板块的进度
export function clearSectionProgress(bigSubject, mode, section) {
  const store = getProgressStore()
  const key = makeProgressKey(bigSubject, mode, section)
  delete store.sections[key]
  // 如果清除的是lastActive，也清除lastActive
  if (store.lastActive &&
      store.lastActive.bigSubject === bigSubject &&
      store.lastActive.mode === mode &&
      store.lastActive.section === section) {
    store.lastActive = null
  }
  const ok = set(STORAGE_KEYS.PROGRESS, store)
  notifyCloudSync()
  return ok
}

// 清除所有刷题记录（进度+答题记录），但保留错题本
export function clearAllQuizRecords() {
  localStorage.removeItem(STORAGE_KEYS.PROGRESS)
  localStorage.removeItem(STORAGE_KEYS.ANSWERS)
  notifyCloudSync()
}

// ===== 答题记录 =====
// 结构：{ "公共基础": { "sectionKey": { "题目id": "用户答案" } }, "专业基础": {...} }
export function getAnswers() {
  return get(STORAGE_KEYS.ANSWERS, {})
}

export function saveAnswer(bigSubject, sectionKey, questionId, userAnswer) {
  const all = getAnswers()
  if (!all[bigSubject]) all[bigSubject] = {}
  if (!all[bigSubject][sectionKey]) all[bigSubject][sectionKey] = {}
  all[bigSubject][sectionKey][questionId] = userAnswer
  const ok = set(STORAGE_KEYS.ANSWERS, all)
  notifyCloudSync()
  return ok
}

export function getSectionAnswers(bigSubject, sectionKey) {
  const all = getAnswers()
  return (all[bigSubject] && all[bigSubject][sectionKey]) || {}
}

export function clearSectionAnswers(bigSubject, sectionKey) {
  const all = getAnswers()
  if (all[bigSubject] && all[bigSubject][sectionKey]) {
    delete all[bigSubject][sectionKey]
    set(STORAGE_KEYS.ANSWERS, all)
    notifyCloudSync()
  }
}

// ===== 错题本 =====
// 结构：{ "公共基础": [题目id数组], "专业基础": [题目id数组] }
export function getWrongBook() {
  const stored = get(STORAGE_KEYS.WRONG, {})
  return {
    '公共基础': stored['公共基础'] || [],
    '专业基础': stored['专业基础'] || []
  }
}

export function addWrong(bigSubject, questionId) {
  const wrong = getWrongBook()
  if (!wrong[bigSubject]) wrong[bigSubject] = []
  if (!wrong[bigSubject].includes(questionId)) {
    wrong[bigSubject].push(questionId)
    set(STORAGE_KEYS.WRONG, wrong)
    notifyCloudSync()
  }
}

export function removeWrong(bigSubject, questionId) {
  const wrong = getWrongBook()
  if (wrong[bigSubject]) {
    wrong[bigSubject] = wrong[bigSubject].filter(id => id !== questionId)
    set(STORAGE_KEYS.WRONG, wrong)
    notifyCloudSync()
  }
}

// ===== 板块完成结果（首页显示最近一次正确率）=====
// 结构：{ [bigSubject]: { [sectionKey]: {rate, correct, total, answered, at} } }
export function getSectionResults() {
  return get(STORAGE_KEYS.RESULTS, {})
}

// 记录某板块最近一次完整做完的结果（会覆盖上一次）
export function saveSectionResult(bigSubject, sectionKey, result) {
  const all = getSectionResults()
  if (!all[bigSubject]) all[bigSubject] = {}
  all[bigSubject][sectionKey] = {
    rate: result.rate,
    correct: result.correct,
    total: result.total,
    answered: result.answered,
    at: Date.now()
  }
  const ok = set(STORAGE_KEYS.RESULTS, all)
  notifyCloudSync()
  return ok
}

// 获取某板块最近一次完成结果
export function getSectionResult(bigSubject, sectionKey) {
  const all = getSectionResults()
  return (all[bigSubject] && all[bigSubject][sectionKey]) || null
}

export function isWrong(bigSubject, questionId) {
  const wrong = getWrongBook()
  return wrong[bigSubject] && wrong[bigSubject].includes(questionId)
}

export function clearWrongBook(bigSubject) {
  const wrong = getWrongBook()
  wrong[bigSubject] = []
  set(STORAGE_KEYS.WRONG, wrong)
  notifyCloudSync()
}

// ===== 云端同步（登录后调用）=====

// 登录后从云端拉取数据，覆盖本地
// 返回 true 表示云端有数据并已覆盖本地；false 表示云端无数据
export async function syncFromCloud() {
  const cloud = await pullFromCloud()
  if (!cloud) return false
  if (cloud.progress) set(STORAGE_KEYS.PROGRESS, cloud.progress)
  if (cloud.answers) set(STORAGE_KEYS.ANSWERS, cloud.answers)
  if (cloud.wrong) set(STORAGE_KEYS.WRONG, cloud.wrong)
  if (cloud.results) set(STORAGE_KEYS.RESULTS, cloud.results)
  return true
}

// 把当前本地数据整体推到云端（登录后如果云端空、本地有旧数据时调用）
export async function pushAllToCloud() {
  const { pushToCloud } = await import('./supabase')
  const localData = {
    progress: get(STORAGE_KEYS.PROGRESS, {}),
    answers: get(STORAGE_KEYS.ANSWERS, {}),
    wrong: get(STORAGE_KEYS.WRONG, {}),
    results: get(STORAGE_KEYS.RESULTS, {})
  }
  await pushToCloud(localData)
}

// 退出登录时清空本地业务数据
export function clearLocalData() {
  localStorage.removeItem(STORAGE_KEYS.PROGRESS)
  localStorage.removeItem(STORAGE_KEYS.ANSWERS)
  localStorage.removeItem(STORAGE_KEYS.WRONG)
  localStorage.removeItem(STORAGE_KEYS.RESULTS)
}
