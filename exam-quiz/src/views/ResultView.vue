<template>
  <div class="result-page">
    <div class="result-card">
      <div class="result-icon">{{ result.rate >= 80 ? '🏆' : result.rate >= 60 ? '👍' : '💪' }}</div>
      <h2 class="result-title">
        {{ result.rate >= 80 ? '太棒了！' : result.rate >= 60 ? '继续加油！' : '再接再厉！' }}
      </h2>

      <div class="section-info">
        <span>{{ bigSubject }}</span>
        <span class="divider">|</span>
        <span>{{ section }}</span>
      </div>

      <div class="score-circle">
        <svg width="160" height="160" viewBox="0 0 160 160">
          <circle cx="80" cy="80" r="70" fill="none" stroke="#f0f0f0" stroke-width="12" />
          <circle
            cx="80" cy="80" r="70" fill="none"
            :stroke="result.rate >= 80 ? '#52c41a' : result.rate >= 60 ? '#faad14' : '#ff4d4f'"
            stroke-width="12"
            stroke-linecap="round"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="circumference - (circumference * result.rate / 100)"
            transform="rotate(-90 80 80)"
          />
        </svg>
        <div class="score-text">
          <span class="score-num">{{ result.rate }}</span>
          <span class="score-unit">%</span>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-num total">{{ result.total }}</div>
          <div class="stat-label">总题数</div>
        </div>
        <div class="stat-item">
          <div class="stat-num correct">{{ result.correct }}</div>
          <div class="stat-label">答对</div>
        </div>
        <div class="stat-item">
          <div class="stat-num wrong">{{ result.wrong }}</div>
          <div class="stat-label">答错</div>
        </div>
        <div class="stat-item">
          <div class="stat-num answered">{{ result.answered }}</div>
          <div class="stat-label">已答</div>
        </div>
      </div>

      <div class="action-buttons">
        <button class="btn primary" @click="retry">重新练习</button>
        <button v-if="isWrongMode" class="btn" @click="removeCorrectFromWrong">从错题本中移除答对的题目</button>
        <button v-else-if="isFavMode" class="btn" @click="removeCorrectFromFav">从收藏夹中移出答对的题目</button>
        <button v-else class="btn" @click="goWrongBook">查看错题</button>
        <button class="btn" @click="goBack">返回</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getQuestionsBySmallSubject,
  getQuestionsByYear,
  getQuestionsByIds,
  calcCorrectRate,
  makeSectionKey
} from '../utils/quiz'
import {
  getSectionAnswers, getWrongBook, getFavorites, clearSectionProgress, clearSectionAnswers,
  removeWrong, removeFavorite, saveSectionResult
} from '../utils/storage'

const route = useRoute()
const router = useRouter()

const bigSubject = ref(route.query.bigSubject || '')
const mode = ref(route.query.mode || '')
const section = ref(route.query.section || '')
const questions = ref([])

const circumference = 2 * Math.PI * 70

// 是否为「错题本查看结果页」
const isWrongMode = computed(() => mode.value === 'wrong')
// 是否为「收藏夹练习结果页」
const isFavMode = computed(() => mode.value === 'fav')

const sectionKey = computed(() => makeSectionKey(mode.value, section.value))

const result = computed(() => {
  const answers = getSectionAnswers(bigSubject.value, sectionKey.value)
  return calcCorrectRate(questions.value, answers)
})

onMounted(() => {
  loadQuestions()
  // 记录该板块最近一次完整做完的结果（供首页显示正确率）
  recordSectionResult()
  // 清除该板块的进度标记（已完成）
  clearSectionProgress(bigSubject.value, mode.value, section.value)
})

function recordSectionResult() {
  const answers = getSectionAnswers(bigSubject.value, sectionKey.value)
  const res = calcCorrectRate(questions.value, answers)
  saveSectionResult(bigSubject.value, sectionKey.value, res)
}

function loadQuestions() {
  if (mode.value === 'smallSubject') {
    questions.value = getQuestionsBySmallSubject(bigSubject.value, section.value)
  } else if (mode.value === 'year') {
    questions.value = getQuestionsByYear(bigSubject.value, section.value)
  } else if (mode.value === 'wrong') {
    const wrong = getWrongBook()
    const ids = wrong[bigSubject.value] || []
    questions.value = getQuestionsByIds(bigSubject.value, ids)
  } else if (mode.value === 'fav') {
    const fav = getFavorites()
    const ids = fav[bigSubject.value] || []
    questions.value = getQuestionsByIds(bigSubject.value, ids)
  }
}

function retry() {
  // 重新练习：清除该板块的答题记录，允许重新作答
  // 用 replace：结果页被做题页替换，历史栈不增长，返回逻辑保持正确
  clearSectionAnswers(bigSubject.value, sectionKey.value)
  router.replace({
    path: '/quiz',
    query: {
      bigSubject: bigSubject.value,
      mode: mode.value,
      section: section.value
    }
  })
}

// 错题本查看结果页：从错题本中移除本次答对的题目，仅保留答错的
function removeCorrectFromWrong() {
  const answers = getSectionAnswers(bigSubject.value, sectionKey.value)
  let removed = 0
  for (const q of questions.value) {
    const userAns = answers[q.id]
    if (userAns && userAns === q.answer) {
      removeWrong(bigSubject.value, q.id)
      removed++
    }
  }
  if (removed > 0) {
    alert(`已从错题本中移除 ${removed} 道本次答对的题目`)
  } else {
    alert('本次没有答对的题目可移除')
  }
}

function goWrongBook() {
  router.push('/wrongbook')
}

// 收藏夹练习结果页：从收藏夹中移出本次答对的题目，仅保留答错的
function removeCorrectFromFav() {
  const answers = getSectionAnswers(bigSubject.value, sectionKey.value)
  let removed = 0
  for (const q of questions.value) {
    const userAns = answers[q.id]
    if (userAns && userAns === q.answer) {
      removeFavorite(bigSubject.value, q.id)
      removed++
    }
  }
  if (removed > 0) {
    alert(`已从收藏夹中移出 ${removed} 道本次答对的题目`)
  } else {
    alert('本次没有答对的题目可移出')
  }
}

// 返回：错题本/收藏夹练习回到各自的列表页（用 back 弹回历史栈中已有的那一层，
// 使列表页的“返回上一步”能继续回到进入列表页前的首页）；套题回到首页第三步
function goBack() {
  if (mode.value === 'wrong' || mode.value === 'fav') {
    if (window.history.length > 1) {
      router.back()
    } else {
      router.push(mode.value === 'wrong' ? '/wrongbook' : '/favorites')
    }
  } else {
    // 保留 quiz_home_state，回到首页第三步
    router.push('/')
  }
}
</script>

<style scoped>
.result-page {
  max-width: 560px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.result-card {
  width: 100%;
  background: #fff;
  border-radius: 16px;
  padding: 30px 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  text-align: center;
}

.result-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.result-title {
  font-size: 22px;
  color: #333;
  margin: 0 0 8px;
}

.section-info {
  color: #888;
  font-size: 14px;
  margin-bottom: 24px;
}

.divider {
  margin: 0 8px;
  color: #ddd;
}

.score-circle {
  position: relative;
  width: 160px;
  height: 160px;
  margin: 0 auto 24px;
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.score-num {
  font-size: 40px;
  font-weight: bold;
  color: #333;
}

.score-unit {
  font-size: 18px;
  color: #888;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.stat-item {
  padding: 12px 4px;
  background: #f8f9fa;
  border-radius: 10px;
}

.stat-num {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 4px;
}

.stat-num.total { color: #4a90d9; }
.stat-num.correct { color: #52c41a; }
.stat-num.wrong { color: #ff4d4f; }
.stat-num.answered { color: #faad14; }

.stat-label {
  font-size: 12px;
  color: #888;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  color: #666;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:hover {
  border-color: #4a90d9;
  color: #4a90d9;
}

.btn.primary {
  background: #4a90d9;
  color: #fff;
  border-color: #4a90d9;
}

.btn.primary:hover {
  background: #357abd;
  color: #fff;
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
