<template>
  <div class="suggest-page">
    <div class="page-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h2 class="page-title">意见建议</h2>
    </div>

    <div class="suggest-card">
      <p class="suggest-tip">您的建议对我们非常重要，欢迎提出软件使用中的改进想法。</p>
      <textarea
        v-model="content"
        class="suggest-input"
        rows="5"
        maxlength="500"
        placeholder="请输入您的建议（最多 500 字）"
      ></textarea>
      <div class="suggest-footer">
        <span class="counter">{{ content.length }}/500</span>
        <button class="submit-btn" :disabled="submitting || !content.trim()" @click="submit">
          {{ submitting ? '提交中...' : '提交建议' }}
        </button>
      </div>
      <div class="success" v-if="success">提交成功，感谢您的建议！</div>
    </div>

    <div class="history" v-if="suggestions.length">
      <h3 class="history-title">我提交过的建议</h3>
      <div class="his-item" v-for="s in suggestions" :key="s.id">
        <div class="his-head">
          <span class="his-time">{{ formatTime(s.created_at) }}</span>
          <span class="his-status" :class="s.status">{{ statusText(s.status) }}</span>
        </div>
        <div class="his-content">{{ s.content }}</div>
      </div>
    </div>

    <div class="loading" v-if="loading">加载中...</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { submitSuggestion, fetchSuggestions } from '../utils/supabase'
import { showToast } from '../utils/toast'

const router = useRouter()
const content = ref('')
const submitting = ref(false)
const success = ref(false)
const suggestions = ref([])
const loading = ref(false)

function goBack() {
  router.replace('/')
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes())
}

function statusText(status) {
  if (status === 'done') return '已采纳'
  if (status === 'processing') return '处理中'
  return '待处理'
}

async function submit() {
  if (!content.value.trim()) return
  submitting.value = true
  success.value = false
  try {
    await submitSuggestion(content.value.trim())
    content.value = ''
    success.value = true
    showToast('提交成功，感谢您的建议！', 1000)
    await load()
  } catch (e) {
    showToast(e.message || '提交失败，请重试', 1500)
  } finally {
    submitting.value = false
  }
}

async function load() {
  loading.value = true
  try {
    suggestions.value = await fetchSuggestions()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.suggest-page {
  max-width: 560px;
  margin: 0 auto;
  padding: 16px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.back-btn {
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
}
.back-btn:hover {
  background: #f5f5f5;
}

.page-title {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.suggest-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.suggest-tip {
  margin: 0 0 12px;
  font-size: 13px;
  color: #888;
}

.suggest-input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  outline: none;
  resize: vertical;
  font-family: inherit;
}
.suggest-input:focus {
  border-color: #4a90d9;
}

.suggest-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.counter {
  font-size: 12px;
  color: #bbb;
}

.submit-btn {
  padding: 8px 20px;
  background: #4a90d9;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}
.submit-btn:hover:not(:disabled) {
  background: #357abd;
}
.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.success {
  margin-top: 12px;
  font-size: 13px;
  color: #52c41a;
  text-align: center;
}

.history {
  margin-top: 20px;
}

.history-title {
  font-size: 15px;
  color: #333;
  margin: 0 0 10px;
}

.his-item {
  background: #fff;
  border-radius: 10px;
  padding: 12px 14px;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 8px;
}

.his-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.his-time {
  font-size: 12px;
  color: #999;
}

.his-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #f0f0f0;
  color: #888;
}
.his-status.done {
  background: #e8f7ee;
  color: #00b42a;
}
.his-status.processing {
  background: #fff7e8;
  color: #ff7d00;
}

.his-content {
  font-size: 13px;
  color: #555;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.loading {
  text-align: center;
  color: #999;
  padding: 30px 0;
  font-size: 14px;
}
</style>
