<template>
  <div class="quiz-page">
    <!-- 顶部导航 -->
    <div class="quiz-header">
      <div class="header-left">
        <button class="nav-button back-btn" @click="goBack">
          <span class="btn-icon">←</span>
          <span class="btn-text">返回上一步</span>
        </button>
        <button class="nav-button select-btn" @click="showPicker = true">
          <span class="btn-icon">📋</span>
          <span class="btn-text">选题</span>
        </button>
      </div>
      <div class="quiz-info">
        <span class="big-subject">{{ bigSubject }}</span>
        <span class="divider">|</span>
        <span class="section">{{ section }}</span>
      </div>
      <div class="header-right">
        <button class="nav-button redo-btn" @click="redoSection">
          <span class="btn-icon">🔄</span>
          <span class="btn-text">重做本套题</span>
        </button>
        <button class="nav-button home-btn" @click="goHome">
          <span class="btn-icon">🏠</span>
          <span class="btn-text">首页</span>
        </button>
      </div>
    </div>

    <!-- 进度条 -->
    <ProgressBar :current="currentIndex + 1" :total="questions.length" />

    <!-- 题目卡片 -->
    <QuestionCard
      v-if="currentQuestion"
      :question="currentQuestion"
      :current-index="currentIndex"
      :total="questions.length"
      :locked="isLocked"
      :initial-answer="currentUserAnswer"
      :is-fav="currentIsFav"
      :is-last="currentIndex === questions.length - 1"
      @submit="handleSubmit"
      @next="handleNext"
      @select="handleSelect"
      @analysis="openAnalysis"
      @toggle-favorite="toggleCurrentFavorite"
    />

    <!-- 底部导航 -->
    <div class="quiz-footer" v-if="currentQuestion">
      <button class="nav-btn prev-btn" :disabled="currentIndex === 0" @click="prevQuestion">
        ← 上一题
      </button>
      <span class="nav-info">{{ currentIndex + 1 }} / {{ questions.length }}</span>
      <button class="nav-btn next-btn" @click="handleNext">
        {{ currentIndex === questions.length - 1 ? '完成' : '下一题 →' }}
      </button>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">📭</div>
      <p>暂无题目</p>
      <button class="back-home-btn" @click="goHome">返回首页</button>
    </div>

    <!-- 答案解析弹窗 -->
    <ResultModal
      :visible="showModal"
      :question="currentQuestion"
      :user-answer="selectedAnswer"
      :is-last="currentIndex === questions.length - 1"
      @close="closeModal"
      @next="handleNext"
    />

    <!-- 选题弹窗 -->
    <div class="picker-mask" v-if="showPicker" @click.self="showPicker = false">
      <div class="picker-modal">
        <div class="picker-header">
          <h3>选择题目</h3>
          <button class="picker-close" @click="showPicker = false">×</button>
        </div>
        <div class="picker-legend">
          <span class="legend-item"><span class="dot unanswered"></span>未做</span>
          <span class="legend-item"><span class="dot correct"></span>正确</span>
          <span class="legend-item"><span class="dot wrong"></span>错误</span>
          <span class="legend-item"><span class="dot current"></span>当前</span>
        </div>
        <div class="picker-grid">
          <button
            v-for="(q, idx) in questions"
            :key="q.id"
            class="picker-item"
            :class="{
              correct: pickerStatus(q.id) === 'correct',
              wrong: pickerStatus(q.id) === 'wrong',
              current: idx === currentIndex
            }"
            @click="jumpTo(idx)"
          >{{ idx + 1 }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import QuestionCard from '../components/QuestionCard.vue'
import ResultModal from '../components/ResultModal.vue'
import ProgressBar from '../components/ProgressBar.vue'
import {
  getQuestionsBySmallSubject,
  getQuestionsByYear,
  getQuestionsByIds,
  makeSectionKey
} from '../utils/quiz'
import {
  getSectionProgress, setProgress, clearSectionProgress,
  saveAnswer, getSectionAnswers, clearSectionAnswers,
  addWrong, getWrongBook, getFavorites, isFavorite, toggleFavorite
} from '../utils/storage'

const route = useRoute()
const router = useRouter()

const bigSubject = ref(route.query.bigSubject || '')
const mode = ref(route.query.mode || '')
const section = ref(route.query.section || '')
const questions = ref([])
const currentIndex = ref(0)
const selectedAnswer = ref('')
const isLocked = ref(false)
const showModal = ref(false)
const showPicker = ref(false)

const sectionKey = computed(() => makeSectionKey(mode.value, section.value))

// "我不会"的答题记录哨兵值（统计时等同答错）
const DONT_KNOW = '__DONT_KNOW__'

const currentQuestion = computed(() => questions.value[currentIndex.value])

const currentUserAnswer = computed(() => {
  if (!currentQuestion.value) return ''
  const answers = getSectionAnswers(bigSubject.value, sectionKey.value)
  const a = answers[currentQuestion.value.id] || ''
  return a === DONT_KNOW ? '' : a
})

// 当前题是否已收藏（favTick 用于切换后触发重算）
const favTick = ref(0)
const currentIsFav = computed(() => {
  favTick.value
  if (!currentQuestion.value) return false
  return isFavorite(bigSubject.value, currentQuestion.value.id)
})

function toggleCurrentFavorite() {
  if (!currentQuestion.value) return
  toggleFavorite(bigSubject.value, currentQuestion.value.id)
  favTick.value++
}

onMounted(() => {
  loadQuestions()
  // 其他设备更新了收藏/错题等数据时，刷新当前题的收藏状态
  window.addEventListener('cloud-data-updated', onCloudUpdate)
  // 电脑端：← 上一题，→ 下一题
  window.addEventListener('keydown', onKeyNav)
})

onUnmounted(() => {
  window.removeEventListener('cloud-data-updated', onCloudUpdate)
  window.removeEventListener('keydown', onKeyNav)
})

function onKeyNav(e) {
  if (e.defaultPrevented) return
  // 图片放大遮罩打开时不切题
  if (document.querySelector('.img-zoom-mask')) return
  if (showPicker.value) return
  if (e.key === 'ArrowLeft') {
    e.preventDefault()
    prevQuestion()
  } else if (e.key === 'ArrowRight') {
    e.preventDefault()
    handleNext()
  }
}

function onCloudUpdate() {
  favTick.value++
}

watch(() => route.query, () => {
  bigSubject.value = route.query.bigSubject || ''
  mode.value = route.query.mode || ''
  section.value = route.query.section || ''
  loadQuestions()
}, { deep: true })

function loadQuestions() {
  if (mode.value === 'smallSubject') {
    questions.value = getQuestionsBySmallSubject(bigSubject.value, section.value)
  } else if (mode.value === 'year') {
    questions.value = getQuestionsByYear(bigSubject.value, section.value)
  } else if (mode.value === 'wrong') {
    // 错题练习模式：清除之前的答题记录，允许重新作答
    clearSectionAnswers(bigSubject.value, sectionKey.value)
    const wrong = getWrongBook()
    const ids = wrong[bigSubject.value] || []
    questions.value = getQuestionsByIds(bigSubject.value, ids)
  } else if (mode.value === 'fav') {
    // 收藏练习模式
    clearSectionAnswers(bigSubject.value, sectionKey.value)
    const fav = getFavorites()
    const ids = fav[bigSubject.value] || []
    questions.value = getQuestionsByIds(bigSubject.value, ids)
  }

  // 恢复该板块的独立进度（每个大科目+模式+板块各自保存进度）
  const sectionProgress = getSectionProgress(bigSubject.value, mode.value, section.value)
  if (sectionProgress) {
    currentIndex.value = sectionProgress.currentIndex || 0
  } else {
    currentIndex.value = 0
  }

  // 支持从指定题目开始（错题本单题练习）
  if (route.query.startIndex) {
    currentIndex.value = parseInt(route.query.startIndex) || 0
  }

  // 恢复当前题的答题状态
  restoreAnswerState()
}

function restoreAnswerState() {
  const answers = getSectionAnswers(bigSubject.value, sectionKey.value)
  const a = currentQuestion.value ? answers[currentQuestion.value.id] : null
  if (a && a !== DONT_KNOW) {
    selectedAnswer.value = a
    isLocked.value = true
  } else if (a === DONT_KNOW) {
    selectedAnswer.value = ''
    isLocked.value = true
  } else {
    selectedAnswer.value = ''
    isLocked.value = false
  }
}

function handleSelect(answer) {
  selectedAnswer.value = answer
}

function handleSubmit(dontKnow = false) {
  if (isLocked.value) return
  if (!dontKnow && !selectedAnswer.value) return

  isLocked.value = true

  // 保存答题记录（"我不会"记为哨兵值，统计时等同答错）
  saveAnswer(bigSubject.value, sectionKey.value, currentQuestion.value.id, dontKnow ? DONT_KNOW : selectedAnswer.value)

  // 答错或"我不会"均加入错题本
  if (dontKnow || selectedAnswer.value !== currentQuestion.value.answer) {
    addWrong(bigSubject.value, currentQuestion.value.id)
  }

  // 保存进度
  setProgress({
    bigSubject: bigSubject.value,
    mode: mode.value,
    section: section.value,
    currentIndex: currentIndex.value
  })

  // 提交后自动弹出解析（保持原有行为）
  showModal.value = true
}

// 点击「查看解析」按钮时打开解析弹窗
function openAnalysis() {
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

function handleNext() {
  showModal.value = false

  if (currentIndex.value >= questions.value.length - 1) {
    // 完成所有题目，跳转到结果页
    router.push({
      path: '/result',
      query: {
        bigSubject: bigSubject.value,
        mode: mode.value,
        section: section.value
      }
    })
    return
  }

  currentIndex.value++
  restoreAnswerState()

  // 更新进度
  setProgress({
    bigSubject: bigSubject.value,
    mode: mode.value,
    section: section.value,
    currentIndex: currentIndex.value
  })
}

function prevQuestion() {
  if (currentIndex.value <= 0) return
  showModal.value = false
  currentIndex.value--
  restoreAnswerState()
  setProgress({
    bigSubject: bigSubject.value,
    mode: mode.value,
    section: section.value,
    currentIndex: currentIndex.value
  })
}

function jumpTo(idx) {
  showPicker.value = false
  currentIndex.value = idx
  restoreAnswerState()
  setProgress({
    bigSubject: bigSubject.value,
    mode: mode.value,
    section: section.value,
    currentIndex: currentIndex.value
  })
}

function pickerStatus(id) {
  const answers = getSectionAnswers(bigSubject.value, sectionKey.value)
  const userAns = answers[id]
  if (!userAns) return 'unanswered'
  const q = questions.value.find(item => item.id === id)
  return q && userAns === q.answer ? 'correct' : 'wrong'
}

function redoSection() {
  if (confirm('确定重做本套题吗？将清除本套题的所有答题记录，错题本保留。')) {
    clearSectionAnswers(bigSubject.value, sectionKey.value)
    clearSectionProgress(bigSubject.value, mode.value, section.value)
    currentIndex.value = 0
    selectedAnswer.value = ''
    isLocked.value = false
    showModal.value = false
  }
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

function goHome() {
  localStorage.removeItem('quiz_home_state')
  router.push('/')
}
</script>

<style scoped>
.quiz-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 16px;
  min-height: 100vh;
}

.quiz-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  cursor: pointer;
  font-size: 13px;
  padding: 4px 10px;
  border-radius: 6px;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.btn-text {
  line-height: 1.2;
}

.back-btn {
  border: none;
  color: #4a90d9;
  font-size: 15px;
  padding: 6px 0;
}

.home-btn {
  border: 1px solid #4a90d9;
  color: #4a90d9;
}

.home-btn:hover {
  background: #4a90d9;
  color: #fff;
}

.quiz-info {
  flex: 1;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.big-subject {
  font-weight: bold;
  color: #333;
}

.divider {
  margin: 0 8px;
  color: #ccc;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.select-btn {
  border: 1px solid #4a90d9;
  color: #4a90d9;
}

.select-btn:hover {
  background: #4a90d9;
  color: #fff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.redo-btn {
  border: 1px solid #faad14;
  color: #faad14;
}

.redo-btn:hover {
  background: #faad14;
  color: #fff;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #fff;
  border-radius: 12px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  color: #888;
  font-size: 16px;
  margin-bottom: 20px;
}

.back-home-btn {
  padding: 10px 30px;
  background: #4a90d9;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
}

.quiz-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  padding: 12px 0;
  gap: 12px;
}

.nav-btn {
  padding: 10px 20px;
  border: 1px solid #4a90d9;
  background: #fff;
  color: #4a90d9;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 100px;
}

.nav-btn:hover:not(:disabled) {
  background: #4a90d9;
  color: #fff;
}

.nav-btn:disabled {
  border-color: #d9d9d9;
  color: #d9d9d9;
  cursor: not-allowed;
}

.next-btn {
  background: #4a90d9;
  color: #fff;
}

.next-btn:hover:not(:disabled) {
  background: #357abd;
}

.nav-info {
  font-size: 14px;
  color: #999;
  flex: 1;
  text-align: center;
}

/* 选题弹窗 */
.picker-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.picker-modal {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.picker-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.picker-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  line-height: 1;
  padding: 0 4px;
}

.picker-close:hover {
  color: #333;
}

.picker-legend {
  display: flex;
  gap: 16px;
  padding: 12px 20px;
  background: #f8f9fa;
  font-size: 13px;
  color: #666;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  display: inline-block;
}

.dot.unanswered {
  background: #e8e8e8;
}

.dot.correct {
  background: #52c41a;
}

.dot.wrong {
  background: #ff4d4f;
}

.dot.current {
  background: #4a90d9;
}

.picker-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(44px, 1fr));
  gap: 8px;
  padding: 16px 20px;
  overflow-y: auto;
  flex: 1;
}

.picker-item {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.picker-item:hover {
  border-color: #4a90d9;
  color: #4a90d9;
}

.picker-item.correct {
  background: #f6ffed;
  border-color: #b7eb8f;
  color: #52c41a;
}

.picker-item.wrong {
  background: #fff2f0;
  border-color: #ffccc7;
  color: #ff4d4f;
}

.picker-item.current {
  background: #4a90d9;
  border-color: #4a90d9;
  color: #fff;
}

@media (max-width: 600px) {
  .quiz-page {
    padding: 12px;
  }
  .picker-grid {
    grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
    gap: 6px;
    padding: 12px;
  }
  .quiz-footer {
    position: sticky;
    bottom: 0;
    background: #f5f5f8;
    padding: 12px;
    margin: 20px -12px -12px;
    border-top: 1px solid #e8e8e8;
  }
  .nav-btn {
    padding: 10px 16px;
    font-size: 14px;
    min-width: 90px;
  }
}

@media (max-width: 480px) and (orientation: portrait) {
  .quiz-header {
    gap: 6px;
    margin-bottom: 10px;
  }
  .nav-button {
    flex-direction: column;
    padding: 6px 4px;
    font-size: 11px;
    gap: 2px;
    min-width: 36px;
  }
  .btn-icon {
    font-size: 16px;
  }
  .btn-text {
    writing-mode: vertical-rl;
    text-orientation: upright;
    letter-spacing: 1px;
    line-height: 1.1;
  }
  .back-btn {
    font-size: 11px;
    padding: 6px 4px;
  }
  .quiz-info {
    font-size: 12px;
  }
  .header-left,
  .header-right {
    gap: 4px;
  }
}
</style>
