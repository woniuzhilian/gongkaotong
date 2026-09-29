<template>
  <div id="app">
    <!-- 顶部用户栏（只在首页显示） -->
    <div class="user-bar" v-if="userPhone && isHomePage">
      <span class="user-phone">👤 {{ userPhone }}</span>
      <button class="logout-btn" @click="logout">退出登录</button>
    </div>

    <router-view />

    <!-- 版本更新提示弹窗 -->
    <div class="update-mask" v-if="showUpdate" @click.self="dismissUpdate">
      <div class="update-modal">
        <div class="update-icon">🎉</div>
        <h3 class="update-title">发现新版本</h3>
        <p class="update-version" v-if="updateInfo.version">v{{ updateInfo.version }}</p>
        <ul class="update-notes" v-if="updateInfo.notes && updateInfo.notes.length">
          <li v-for="(note, i) in updateInfo.notes" :key="i">{{ note }}</li>
        </ul>
        <div class="update-actions">
          <button class="update-later" @click="dismissUpdate">稍后再说</button>
          <button class="update-refresh" @click="applyUpdate">立即刷新</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getCurrentUser, signOut, onAuthStateChange, subscribeToProgress, unsubscribeProgress, getMySessionId, markMySessionOnline, clearMySession } from './utils/supabase'
import { clearLocalData, syncFromCloud } from './utils/storage'
import { setLoginState } from './main'

const router = useRouter()
const userPhone = ref('')
const currentRoute = ref('/')

// ===== 版本更新提示 =====
const showUpdate = ref(false)
const updateInfo = ref({})
// 同一版本只提示一次
const SEEN_KEY = 'seen_update_version'

async function loadChangelog() {
  try {
    const res = await fetch('/changelog.json', { cache: 'no-cache' })
    if (res.ok) updateInfo.value = await res.json()
  } catch (e) {
    // 拉不到更新日志也照常弹窗，只是没有说明
  }
}

function onUpdateAvailable() {
  const v = updateInfo.value.version || 'unknown'
  if (localStorage.getItem(SEEN_KEY) === v) return
  showUpdate.value = true
}

async function dismissUpdate() {
  showUpdate.value = false
  localStorage.setItem(SEEN_KEY, updateInfo.value.version || 'unknown')
}

async function applyUpdate() {
  localStorage.setItem(SEEN_KEY, updateInfo.value.version || 'unknown')
  // 通知 waiting 的 service worker 立即激活，然后刷新页面
  try {
    const reg = await navigator.serviceWorker.getRegistration()
    if (reg && reg.waiting) reg.waiting.postMessage({ type: 'SKIP_WAITING' })
  } catch (e) {}
  setTimeout(() => window.location.reload(), 150)
}

// 只在首页显示用户栏
const isHomePage = computed(() => currentRoute.value === '/')

// 收到其他设备的更新：把云端最新数据写入本地，然后通知页面刷新
async function handleRemoteUpdate(payload) {
  await syncFromCloud()
  window.dispatchEvent(new CustomEvent('cloud-data-updated'))
}

// 被挤下线时强制退出
async function forceLogout() {
  try { await signOut() } catch (e) {}
  clearLocalData()
  clearMySession()
  setLoginState(false)
  userPhone.value = ''
  router.push('/auth')
}

onMounted(async () => {
  currentRoute.value = router.currentRoute.value.path

  // 更新提示：先拉更新日志，再检查是否已有待激活的新版本
  await loadChangelog()
  window.addEventListener('sw-update-available', onUpdateAvailable)
  try {
    const reg = await navigator.serviceWorker.getRegistration()
    if (reg && reg.waiting) onUpdateAvailable()
  } catch (e) {}

  const user = await getCurrentUser()
  if (user) {
    userPhone.value = user.phone
    await markMySessionOnline()
    subscribeToProgress(user.userId, handleRemoteUpdate)
  }

  onAuthStateChange((u) => {
    userPhone.value = u?.phone || ''
    if (u) {
      subscribeToProgress(u.userId, handleRemoteUpdate)
    } else {
      unsubscribeProgress()
    }
  })

  // 监听路由变化
  router.afterEach((to) => {
    currentRoute.value = to.path
  })
})

onUnmounted(() => {
  unsubscribeProgress()
  window.removeEventListener('sw-update-available', onUpdateAvailable)
})

async function logout() {
  if (!confirm('确定退出登录吗？本地进度已同步到云端，下次登录可恢复。')) return
  try {
    await signOut()
  } catch (e) {
    console.error('登出失败:', e)
  }
  clearLocalData()
  clearMySession()
  setLoginState(false)
  userPhone.value = ''
  router.push('/auth')
}
</script>

<style>
/* 全局样式在 style.css 中定义 */
</style>

<style scoped>
.user-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.user-phone {
  font-size: 13px;
  color: #666;
}

.logout-btn {
  background: none;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
}

.logout-btn:hover {
  background: #ff4d4f;
  color: #fff;
}

/* 版本更新弹窗 */
.update-mask {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.update-modal {
  background: #fff;
  border-radius: 14px;
  padding: 24px 20px 20px;
  width: min(86vw, 360px);
  text-align: center;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.update-icon {
  font-size: 36px;
  margin-bottom: 6px;
}

.update-title {
  margin: 0 0 4px;
  font-size: 18px;
  color: #333;
}

.update-version {
  margin: 0 0 12px;
  font-size: 12px;
  color: #999;
}

.update-notes {
  margin: 0 0 18px;
  padding: 12px 14px 12px 30px;
  background: #f7f9fc;
  border-radius: 8px;
  text-align: left;
  font-size: 13px;
  color: #555;
  line-height: 1.8;
  max-height: 40vh;
  overflow-y: auto;
}

.update-actions {
  display: flex;
  gap: 10px;
}

.update-later {
  flex: 1;
  padding: 10px;
  background: #f5f5f5;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
}

.update-refresh {
  flex: 1;
  padding: 10px;
  background: #4a90d9;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  color: #fff;
  cursor: pointer;
}

.update-refresh:hover {
  background: #357abd;
}
</style>
