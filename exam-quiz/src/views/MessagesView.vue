<template>
  <div class="messages-page">
    <div class="page-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h2 class="page-title">消息</h2>
      <button class="refresh-btn" @click="load" :disabled="loading">刷新</button>
    </div>

    <div class="msg-list" v-if="messages.length">
      <div
        class="msg-item"
        :class="{ unread: !m.is_read }"
        v-for="m in messages"
        :key="m.id"
        @click="openMessage(m)"
      >
        <div class="msg-head">
          <span class="msg-title">{{ m.title }}</span>
          <span class="msg-dot" v-if="!m.is_read"></span>
        </div>
        <div class="msg-time">{{ formatTime(m.created_at) }}</div>
        <div class="msg-preview" v-if="!expandedId || expandedId !== m.id">{{ m.content }}</div>
        <div class="msg-content" v-else>{{ m.content }}</div>
      </div>
    </div>

    <div class="empty" v-else-if="!loading">
      <div class="empty-icon">📭</div>
      <p>暂无消息</p>
      <p class="empty-tip">您反馈的题目被修复后，系统会在这里给您发送通知</p>
    </div>

    <div class="loading" v-if="loading">加载中...</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchMessages, markMessageRead } from '../utils/supabase'

const router = useRouter()
const messages = ref([])
const loading = ref(false)
const expandedId = ref(null)

function goBack() {
  window.dispatchEvent(new CustomEvent('refresh-unread'))
  router.replace('/')
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function openMessage(m) {
  if (expandedId.value === m.id) {
    expandedId.value = null
    return
  }
  expandedId.value = m.id
  if (!m.is_read) {
    m.is_read = true
    try { await markMessageRead(m.id) } catch (e) { console.error(e) }
  }
}

async function load() {
  loading.value = true
  try {
    messages.value = await fetchMessages()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.messages-page {
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
  flex: 1;
}

.refresh-btn {
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
}
.refresh-btn:disabled {
  opacity: 0.5;
}

.msg-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.msg-item {
  background: #fff;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: box-shadow 0.2s;
}
.msg-item:hover {
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
}
.msg-item.unread {
  background: #f0f7ff;
  border: 1px solid #cfe5ff;
}

.msg-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.msg-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.msg-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff4d4f;
  flex-shrink: 0;
}

.msg-time {
  font-size: 12px;
  color: #999;
  margin-bottom: 6px;
}

.msg-preview {
  font-size: 13px;
  color: #666;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.msg-content {
  font-size: 14px;
  color: #333;
  line-height: 1.7;
  white-space: pre-wrap;
}

.empty {
  text-align: center;
  padding: 60px 0;
  color: #999;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 10px;
}
.empty p {
  margin: 4px 0;
  font-size: 14px;
}
.empty-tip {
  font-size: 12px;
  color: #bbb;
}

.loading {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-size: 14px;
}
</style>
