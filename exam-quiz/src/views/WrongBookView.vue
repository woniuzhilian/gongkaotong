<template>
  <div class="wrongbook-page">
    <div class="page-header">
      <button class="back-btn" @click="goBack">← 返回上一步</button>
      <h1>错题本</h1>
      <button class="home-btn" @click="goHome">🏠 首页</button>
    </div>

    <!-- 选择大科目 -->
    <div class="subject-tabs">
      <button
        class="tab-btn"
        :class="{ active: selectedBigSubject === '公共基础' }"
        @click="selectedBigSubject = '公共基础'"
      >
        公共基础
        <span class="count">{{ wrongCounts['公共基础'] }}</span>
      </button>
      <button
        class="tab-btn"
        :class="{ active: selectedBigSubject === '专业基础' }"
        @click="selectedBigSubject = '专业基础'"
      >
        岩土专业基础
        <span class="count">{{ wrongCounts['专业基础'] }}</span>
      </button>
    </div>

    <!-- 错题列表 -->
    <div class="wrong-list" v-if="wrongQuestions.length > 0">
      <div class="wrong-item" v-for="(q, index) in wrongQuestions" :key="q.id">
        <div class="item-header">
          <span class="item-num">{{ index + 1 }}</span>
          <span class="item-subject">{{ q.smallSubject }}</span>
          <span class="item-year">{{ q.year }}-{{ q.id }}</span>
          <button class="practice-btn" @click="practiceOne(index)">练习</button>
          <button class="delete-btn" @click="removeOne(q.id)" title="移出错题本">×</button>
        </div>
        <div class="item-question" v-html="renderQuestion(q.question)"></div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else>
      <div class="empty-icon">🎉</div>
      <p>暂无错题，继续加油！</p>
    </div>

    <!-- 底部操作 -->
    <div class="footer-actions" v-if="wrongQuestions.length > 0">
      <button class="practice-all-btn" @click="practiceAll">
        开始错题练习（{{ wrongQuestions.length }}题）
      </button>
      <button class="clear-btn" @click="clearAll">清空错题本</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import katex from 'katex'
import { getWrongBook, clearWrongBook, removeWrong } from '../utils/storage'
import { getQuestionsByIds } from '../utils/quiz'

const router = useRouter()
const selectedBigSubject = ref('公共基础')
const wrongBook = ref({ '公共基础': [], '专业基础': [] })

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

function goHome() {
  // 清除首页步骤状态，确保真正回到首页第一步
  localStorage.removeItem('quiz_home_state')
  router.push('/')
}

const wrongCounts = computed(() => ({
  '公共基础': wrongBook.value['公共基础']?.length || 0,
  '专业基础': wrongBook.value['专业基础']?.length || 0
}))

const wrongQuestions = computed(() => {
  const ids = wrongBook.value[selectedBigSubject.value] || []
  return getQuestionsByIds(selectedBigSubject.value, ids)
})

onMounted(() => {
  wrongBook.value = getWrongBook()
})

function renderQuestion(text) {
  if (!text) return ''
  return text.replace(/\$([^$]+)\$/g, (match, formula) => {
    try {
      return katex.renderToString('\\displaystyle ' + formula, { throwOnError: false })
    } catch (e) {
      return match
    }
  })
}

function practiceAll() {
  router.push({
    path: '/quiz',
    query: {
      bigSubject: selectedBigSubject.value,
      mode: 'wrong',
      section: '错题本'
    }
  })
}

function practiceOne(index) {
  // 从指定题目开始练习
  router.push({
    path: '/quiz',
    query: {
      bigSubject: selectedBigSubject.value,
      mode: 'wrong',
      section: '错题本',
      startIndex: index
    }
  })
}

function removeOne(questionId) {
  removeWrong(selectedBigSubject.value, questionId)
  wrongBook.value = getWrongBook()
}

function clearAll() {
  if (confirm(`确定清空${selectedBigSubject.value}的所有错题吗？`)) {
    clearWrongBook(selectedBigSubject.value)
    wrongBook.value = getWrongBook()
  }
}
</script>

<style scoped>
.wrongbook-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 16px;
  min-height: 100vh;
  padding-bottom: 100px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.page-header h1 {
  flex: 1;
  text-align: center;
  font-size: 20px;
  margin: 0;
  color: #333;
}

.back-btn {
  background: none;
  border: none;
  color: #4a90d9;
  font-size: 15px;
  cursor: pointer;
}

.home-btn {
  background: none;
  border: 1px solid #4a90d9;
  color: #4a90d9;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 6px;
}

.home-btn:hover {
  background: #4a90d9;
  color: #fff;
}

.subject-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab-btn {
  flex: 1;
  padding: 12px;
  border: 2px solid #e8e8e8;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  font-size: 15px;
  color: #666;
  transition: all 0.2s;
}

.tab-btn.active {
  border-color: #ff4d4f;
  background: #fff2f0;
  color: #ff4d4f;
}

.count {
  display: inline-block;
  background: #ff4d4f;
  color: #fff;
  font-size: 12px;
  padding: 1px 8px;
  border-radius: 10px;
  margin-left: 6px;
}

.tab-btn.active .count {
  background: #ff4d4f;
}

.wrong-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.wrong-item {
  background: #fff;
  border-radius: 10px;
  padding: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.item-num {
  background: #ff4d4f;
  color: #fff;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.item-subject, .item-year {
  font-size: 12px;
  color: #888;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 10px;
}

.practice-btn {
  margin-left: auto;
  background: #4a90d9;
  color: #fff;
  border: none;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}

.delete-btn {
  background: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.delete-btn:hover {
  background: #ff4d4f;
  color: #fff;
}

.item-question {
  font-size: 14px;
  line-height: 1.7;
  color: #333;
  margin-bottom: 8px;
}

.item-question :deep(img) {
  max-width: 100%;
}

.item-answer {
  font-size: 13px;
  color: #666;
}

.correct {
  color: #52c41a;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.footer-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
  max-width: 720px;
  margin: 0 auto;
}

.practice-all-btn {
  flex: 1;
  padding: 12px;
  background: #ff4d4f;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
}

.clear-btn {
  padding: 12px 20px;
  background: #f5f5f5;
  color: #999;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}
</style>
