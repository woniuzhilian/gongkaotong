<template>
  <div class="changelog-page">
    <div class="page-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1>更新日志</h1>
      <button class="home-btn" @click="$router.push('/')">🏠 首页</button>
    </div>

    <div class="cl-tip">当前版本 v{{ currentVersion }}</div>

    <div class="cl-list" v-if="history.length">
      <div class="cl-item" v-for="(entry, i) in history" :key="i">
        <div class="cl-entry-header">
          <span class="cl-date">{{ entry.date }}</span>
          <span class="cl-badge" v-if="entry.version === currentVersion">当前版本</span>
        </div>
        <div class="cl-title">{{ entry.title }}</div>
        <ul class="cl-notes">
          <li v-for="(note, j) in entry.notes" :key="j">{{ note }}</li>
        </ul>
      </div>
    </div>

    <div class="empty-state" v-else-if="!loading">
      <p>暂无更新记录</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const history = ref([])
const currentVersion = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await fetch('/changelog.json', { cache: 'no-cache' })
    if (res.ok) {
      const data = await res.json()
      currentVersion.value = data.version || ''
      history.value = data.history || []
    }
  } catch (e) {
    // 拉取失败保持空状态
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.push('/')
}
</script>

<style scoped>
.changelog-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 16px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.page-header h1 {
  font-size: 20px;
  margin: 0;
}

.back-btn,
.home-btn {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 14px;
}

.cl-tip {
  text-align: center;
  color: #888;
  font-size: 13px;
  margin-bottom: 16px;
}

.cl-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.cl-item {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.cl-entry-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cl-date {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.cl-badge {
  background: #e6f4ff;
  color: #1677ff;
  border: 1px solid #91caff;
  font-size: 12px;
  padding: 1px 8px;
  border-radius: 10px;
}

.cl-title {
  color: #d46b08;
  font-size: 14px;
  margin: 6px 0 8px;
}

.cl-notes {
  margin: 0;
  padding-left: 20px;
  color: #555;
  font-size: 14px;
  line-height: 1.7;
}

.cl-notes li {
  margin-bottom: 4px;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 40px 0;
}
</style>
