<template>
  <div class="home-page">
    <!-- 顶部导航（step2和step3显示） -->
    <div class="top-nav" v-if="step > 1">
      <button class="nav-back" @click="goBackStep">← 返回上一步</button>
      <button class="nav-home" @click="goHome">🏠 首页</button>
    </div>

    <div class="header">
      <h1>工考通·岩土</h1>
      <p class="subtitle">公共基础 + 岩土专业基础 · 历年真题</p>
    </div>

    <!-- 导航按钮 -->
    <div class="nav-buttons">
      <button class="nav-btn wrong" @click="goWrongBook">
        <span class="nav-icon">📝</span>
        <span>错题本</span>
        <span class="wrong-count" v-if="totalWrong > 0">{{ totalWrong }}题</span>
      </button>
    </div>

    <!-- 第一步：选择大科目 -->
    <div class="section" v-if="step === 1">
      <h2 class="section-title">第一步：选择大科目</h2>
      <div class="subject-cards">
        <div
          class="subject-card"
          :class="{ active: selectedBigSubject === '公共基础' }"
          @click="selectBigSubject('公共基础')"
        >
          <div class="card-icon">📚</div>
          <div class="card-title">公共基础</div>
          <div class="card-desc">{{ pubStats.years }}年真题 · {{ pubStats.count }}题</div>
        </div>
        <div
          class="subject-card"
          :class="{ active: selectedBigSubject === '专业基础' }"
          @click="selectBigSubject('专业基础')"
        >
          <div class="card-icon">🏗️</div>
          <div class="card-title">岩土专业基础</div>
          <div class="card-desc">{{ profStats.years }}年真题 · {{ profStats.count }}题</div>
        </div>
      </div>
    </div>

    <!-- 第二步：选择刷题模式 -->
    <div class="section" v-if="step === 2">
      <h2 class="section-title">第二步：选择刷题模式</h2>
      <div class="mode-cards">
        <div
          class="mode-card"
          :class="{ active: selectedMode === 'smallSubject' }"
          @click="selectMode('smallSubject')"
        >
          <div class="mode-icon">📂</div>
          <div class="mode-title">按小科目刷题</div>
          <div class="mode-desc">按知识点分类专项练习</div>
        </div>
        <div
          class="mode-card"
          :class="{ active: selectedMode === 'year' }"
          @click="selectMode('year')"
        >
          <div class="mode-icon">📅</div>
          <div class="mode-title">按年份刷题</div>
          <div class="mode-desc">按年份整套真题练习</div>
        </div>
      </div>
    </div>

    <!-- 第三步：选择小科目/年份 -->
    <div class="section" v-if="step === 3">
      <h2 class="section-title">
        第三步：选择{{ selectedMode === 'smallSubject' ? '小科目' : '年份' }}
      </h2>
      <div class="item-list">
        <div
          v-for="item in itemList"
          :key="item.name || item.year"
          class="item-card"
          @click="startQuiz(item)"
        >
          <span class="item-name">{{ item.name || (item.year + '年') }}</span>
          <span
            v-if="item.result"
            class="item-rate"
            :class="rateClass(item.result.rate)"
          >上次正确率 {{ item.result.rate }}%</span>
          <span class="item-count">{{ item.count }}题</span>
          <span class="item-arrow">→</span>
        </div>
      </div>
    </div>

    <!-- 恢复进度提示 -->
    <div class="resume-tip" v-if="savedProgress && step === 1">
      <span class="resume-text" @click="resumeQuiz">
        📌 检测到上次刷题进度，点击继续
        <span class="resume-info">{{ savedProgress.bigSubject }} · {{ savedProgress.section }}</span>
      </span>
      <button class="restart-btn" @click="restartQuiz">重新开始</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSmallSubjects, getYears, getQuestionsByBigSubject, makeSectionKey } from '../utils/quiz'
import { getProgress, getWrongBook, clearAllQuizRecords, getSectionResult } from '../utils/storage'

const router = useRouter()

const step = ref(1)
const selectedBigSubject = ref('')
const selectedMode = ref('')
const savedProgress = ref(null)
const refreshTick = ref(0)

const HOME_STATE_KEY = 'quiz_home_state'

function saveHomeState() {
  localStorage.setItem(HOME_STATE_KEY, JSON.stringify({
    step: step.value,
    selectedBigSubject: selectedBigSubject.value,
    selectedMode: selectedMode.value
  }))
}

function restoreHomeState() {
  try {
    const saved = localStorage.getItem(HOME_STATE_KEY)
    if (saved) {
      const state = JSON.parse(saved)
      step.value = state.step || 1
      selectedBigSubject.value = state.selectedBigSubject || ''
      selectedMode.value = state.selectedMode || ''
    }
  } catch (e) {
    // ignore
  }
}

function clearHomeState() {
  localStorage.removeItem(HOME_STATE_KEY)
}

function refreshProgress() {
  savedProgress.value = getProgress()
}

function refreshAll() {
  refreshProgress()
  refreshTick.value++
}

function onCloudUpdate() {
  refreshAll()
}

onMounted(() => {
  restoreHomeState()
  refreshProgress()
  window.addEventListener('cloud-data-updated', onCloudUpdate)
})

onUnmounted(() => {
  window.removeEventListener('cloud-data-updated', onCloudUpdate)
})

const totalWrong = computed(() => {
  refreshTick.value
  const wrong = getWrongBook()
  return (wrong['公共基础']?.length || 0) + (wrong['专业基础']?.length || 0)
})

const pubStats = computed(() => {
  const list = getQuestionsByBigSubject('公共基础')
  const years = new Set(list.map(q => q.year))
  return { years: years.size, count: list.length }
})

const profStats = computed(() => {
  const list = getQuestionsByBigSubject('专业基础')
  const years = new Set(list.map(q => q.year))
  return { years: years.size, count: list.length }
})

const itemList = computed(() => {
  refreshTick.value
  if (!selectedBigSubject.value) return []
  const base = selectedMode.value === 'smallSubject'
    ? getSmallSubjects(selectedBigSubject.value)
    : getYears(selectedBigSubject.value)
  // 附加最近一次完整做完该年份/小科目的正确率
  return base.map(item => {
    const sectionValue = item.name || item.year
    const key = makeSectionKey(selectedMode.value, sectionValue)
    const result = getSectionResult(selectedBigSubject.value, key)
    return { ...item, result }
  })
})

function rateClass(rate) {
  if (rate >= 80) return 'rate-good'
  if (rate >= 60) return 'rate-mid'
  return 'rate-bad'
}

function selectBigSubject(subject) {
  selectedBigSubject.value = subject
  step.value = 2
  saveHomeState()
}

function selectMode(mode) {
  selectedMode.value = mode
  step.value = 3
  saveHomeState()
}

function startQuiz(item) {
  const sectionValue = item.name || item.year
  router.push({
    path: '/quiz',
    query: {
      bigSubject: selectedBigSubject.value,
      mode: selectedMode.value,
      section: sectionValue
    }
  })
}

function goWrongBook() {
  router.push('/wrongbook')
}

function resumeQuiz() {
  if (!savedProgress.value) return
  router.push({
    path: '/quiz',
    query: {
      bigSubject: savedProgress.value.bigSubject,
      mode: savedProgress.value.mode,
      section: savedProgress.value.section,
      resume: '1'
    }
  })
}

function restartQuiz() {
  if (confirm('确定重新开始吗？将清除所有刷题进度和答题记录，错题本保留。')) {
    clearAllQuizRecords()
    savedProgress.value = null
  }
}

function goBackStep() {
  if (step.value > 1) {
    step.value--
    saveHomeState()
  }
}

function goHome() {
  step.value = 1
  selectedBigSubject.value = ''
  selectedMode.value = ''
  clearHomeState()
}
</script>

<style scoped>
.home-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.nav-back {
  background: none;
  border: none;
  color: #4a90d9;
  font-size: 15px;
  cursor: pointer;
  padding: 6px 0;
}

.nav-home {
  background: none;
  border: 1px solid #4a90d9;
  color: #4a90d9;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 6px;
}

.nav-home:hover {
  background: #4a90d9;
  color: #fff;
}

.header {
  text-align: center;
  padding: 30px 0 20px;
}

.header h1 {
  font-size: 26px;
  color: #333;
  margin: 0 0 8px;
}

.subtitle {
  color: #888;
  font-size: 14px;
  margin: 0;
}

.nav-buttons {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 20px;
  color: #d46b08;
  cursor: pointer;
  font-size: 14px;
}

.nav-btn:hover {
  background: #ffe7ba;
}

.wrong-count {
  background: #ff4d4f;
  color: #fff;
  font-size: 12px;
  padding: 1px 8px;
  border-radius: 10px;
}

.section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 16px;
  text-align: center;
}

.subject-cards, .mode-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.subject-card, .mode-card {
  background: #fff;
  border: 2px solid #e8e8e8;
  border-radius: 14px;
  padding: 24px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.subject-card:hover, .mode-card:hover {
  border-color: #4a90d9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74,144,217,0.15);
}

.subject-card.active, .mode-card.active {
  border-color: #4a90d9;
  background: #f0f7ff;
}

.card-icon, .mode-icon {
  font-size: 36px;
  margin-bottom: 10px;
}

.card-title, .mode-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 6px;
}

.card-desc, .mode-desc {
  font-size: 13px;
  color: #888;
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item-card {
  display: flex;
  align-items: center;
  padding: 14px 18px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.item-card:hover {
  border-color: #4a90d9;
  background: #f0f7ff;
}

.item-name {
  flex: 1;
  font-size: 15px;
  color: #333;
}

.item-count {
  color: #888;
  font-size: 13px;
  margin-right: 12px;
}

.item-rate {
  font-size: 13px;
  padding: 2px 10px;
  border-radius: 10px;
  margin-right: 12px;
  white-space: nowrap;
}

.item-rate.rate-good {
  color: #52c41a;
  background: #f6ffed;
}

.item-rate.rate-mid {
  color: #faad14;
  background: #fffbe6;
}

.item-rate.rate-bad {
  color: #ff4d4f;
  background: #fff2f0;
}

.item-arrow {
  color: #4a90d9;
  font-size: 18px;
}

.back-btn {
  display: block;
  margin: 20px auto 0;
  background: none;
  border: none;
  color: #888;
  font-size: 14px;
  cursor: pointer;
}

.back-btn:hover {
  color: #4a90d9;
}

.resume-tip {
  margin-top: 30px;
  padding: 14px 18px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.resume-text {
  cursor: pointer;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.resume-text:hover {
  opacity: 0.8;
}

.restart-btn {
  background: #fff;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
}

.restart-btn:hover {
  background: #ff4d4f;
  color: #fff;
}

.resume-info {
  color: #1890ff;
  font-size: 13px;
}

@media (max-width: 600px) {
  .header h1 {
    font-size: 22px;
  }
  .subject-cards, .mode-cards {
    gap: 10px;
  }
  .subject-card, .mode-card {
    padding: 18px 10px;
  }
  .card-icon, .mode-icon {
    font-size: 28px;
  }
}
</style>
