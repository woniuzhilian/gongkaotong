<template>
  <div id="app">
    <!-- 顶部用户栏（只在首页显示） -->
    <div class="user-bar" v-if="(userPhone || isGuest) && isHomePage">
      <!-- 左侧：游客保持原样；登录用户显示「用户中心」按钮（不再显示手机号） -->
      <template v-if="isGuest">
        <span class="user-phone">👤 游客模式</span>
        <button class="logout-btn" @click="logout">退出游客</button>
      </template>
      <div class="user-center" v-else ref="centerEl">
        <button class="center-btn" @click="showCenterMenu = !showCenterMenu">👤 用户中心</button>
        <div class="center-menu" v-if="showCenterMenu" @click="showCenterMenu = false">
          <button class="center-item" @click="goSecurity">🔒 安全中心</button>
          <button class="center-item danger" @click="logout">退出登录</button>
        </div>
      </div>
      <!-- 右侧：音效开关 -->
      <button class="sound-toggle" :class="{ off: soundOff }" @click="toggleSound" :title="soundOff ? '打开音效' : '关闭音效'">
        {{ soundOff ? '🔇 音效关' : '🔊 音效开' }}
      </button>
    </div>

    <router-view />

    <!-- 版本更新提示弹窗 -->
    <div class="update-mask" v-if="showUpdate" @click.self="dismissUpdate">
      <div class="update-modal">
        <div class="update-icon">🎉</div>
        <h3 class="update-title">发现新版本</h3>
        <p class="update-version" v-if="updateInfo.version">v{{ updateInfo.version }}</p>
        <ul class="update-notes" v-if="updateInfo.summary && updateInfo.summary.length">
          <li v-for="(note, i) in updateInfo.summary" :key="i">{{ note }}</li>
        </ul>
        <p class="update-more">查看详细更新内容：首页 → 更新日志</p>
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
import { clearLocalData, syncFromCloud, getProgress } from './utils/storage'
import { setLoginState, setGuestState, guestState } from './main'
import { isMuted, toggleMuted } from './utils/sound'

const router = useRouter()
const userPhone = ref('')
const isGuest = computed(() => guestState.value)
const currentRoute = ref('/')

// ===== 用户中心下拉菜单 =====
const showCenterMenu = ref(false)
const centerEl = ref(null)

function onDocClickCloseMenu(e) {
  if (showCenterMenu.value && centerEl.value && !centerEl.value.contains(e.target)) {
    showCenterMenu.value = false
  }
}

function goSecurity() {
  showCenterMenu.value = false
  router.push('/security')
}

// ===== 音效开关 =====
const soundOff = ref(isMuted())
function toggleSound() {
  soundOff.value = toggleMuted()
}

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
  // 游客状态由 main.js 的 guestState (reactive) 响应式提供，无需这里恢复

  onAuthStateChange((u) => {
    userPhone.value = u?.phone || ''
    if (u) {
      // 登录了就自动退出游客模式
      setGuestState(false)
      subscribeToProgress(u.userId, handleRemoteUpdate)
    } else {
      unsubscribeProgress()
    }
  })

  // 监听路由变化
  router.afterEach((to) => {
    currentRoute.value = to.path
  })

  // 手机端：从屏幕左缘向右滑动 = 返回上一级
  document.addEventListener('touchstart', onSwipeStart, { passive: true })
  document.addEventListener('touchend', onSwipeEnd, { passive: true })
  document.addEventListener('click', onDocClickCloseMenu, true)
})

onUnmounted(() => {
  unsubscribeProgress()
  window.removeEventListener('sw-update-available', onUpdateAvailable)
  document.removeEventListener('touchstart', onSwipeStart)
  document.removeEventListener('touchend', onSwipeEnd)
  document.removeEventListener('click', onDocClickCloseMenu, true)
})

// ===== 手机端滑动导航：左缘右滑返回上一级，右缘左滑回到最近做题界面 =====
let swipeStartX = 0
let swipeStartY = 0
let swipeStartTime = 0
let swipeActive = false
let swipeDir = ''

function onSwipeStart(e) {
  // 草稿纸/弹窗内起笔时，直接看事件目标是否落在遮罩里（比依赖子组件 stopPropagation 更可靠）
  if (e.target && e.target.closest && e.target.closest('.scratch-mask')) {
    swipeActive = false
    swipeDir = ''
    return
  }
  // 有弹窗/图片放大/草稿纸遮罩时不启动边缘滑动
  if (swipeBlocked()) { swipeActive = false; swipeDir = ''; return }
  if (e.touches.length !== 1) { swipeActive = false; return }
  const t = e.touches[0]
  // 只在从屏幕左右边缘 36px 内起手时启用，避免干扰正常滚动
  if (t.clientX <= 36) swipeDir = 'right'
  else if (t.clientX >= window.innerWidth - 36) swipeDir = 'left'
  else swipeDir = ''
  swipeActive = swipeDir !== ''
  swipeStartX = t.clientX
  swipeStartY = t.clientY
  swipeStartTime = Date.now()
}

function onSwipeEnd(e) {
  if (!swipeActive) return
  swipeActive = false
  const t = e.changedTouches[0]
  const dx = t.clientX - swipeStartX
  const dy = t.clientY - swipeStartY
  const dt = Date.now() - swipeStartTime
  // 以水平为主且动作较快
  if (Math.abs(dx) <= 80 || Math.abs(dx) <= Math.abs(dy) * 1.5 || dt >= 500) return
  if (swipeDir === 'right') goBackLevel()
  else if (swipeDir === 'left') goLastQuiz()
}

function swipeBlocked() {
  if (showUpdate.value) return true
  // 有弹窗/图片放大遮罩/草稿/计算器时不触发滑动导航
  if (document.querySelector('.img-zoom-mask, .report-mask, .picker-mask, .update-mask, .analysis-mask, .scratch-mask, .calc-float.open')) return true
  return false
}

function goBackLevel() {
  if (swipeBlocked()) return
  // 结果页：错题本/收藏夹用 sessionStorage 记录的来源精确跳回；套题/小科目 replace('/') 回首页
  if (currentRoute.value === '/result') {
    const returnTo = sessionStorage.getItem('quiz_return_to')
    if (returnTo) {
      sessionStorage.removeItem('quiz_return_to')
      router.replace(returnTo)
    } else {
      router.replace('/')
    }
    return
  }
  // 错题本/收藏夹：replace('/') 回首页（首页有 quiz_home_state 记住第几步）
  // 不用 router.back()，历史栈可能混有 /auth 等无关条目
  if (currentRoute.value === '/wrongbook' || currentRoute.value === '/favorites') {
    router.replace('/')
    return
  }
  // 首页三个步骤都在 / 路由内，右滑 = 返回上一步（由 HomeView 处理）
  if (currentRoute.value === '/') {
    window.dispatchEvent(new CustomEvent('app-swipe-back'))
    return
  }
  // 其他页面：安全起见也 replace('/') 兜底，不依赖历史栈
  router.replace('/')
}

function goLastQuiz() {
  if (swipeBlocked()) return
  if (currentRoute.value === '/quiz') return
  const p = getProgress()
  if (!p || !p.bigSubject) return
  router.push({
    path: '/quiz',
    query: { bigSubject: p.bigSubject, mode: p.mode, section: p.section, resume: '1' }
  })
}

async function logout() {
  showCenterMenu.value = false
  if (isGuest.value) {
    if (!confirm('确定退出游客模式吗？本地数据将保留，但下次进入游客模式前仍为未登录状态。')) return
    setGuestState(false)
    router.push('/auth')
    return
  }
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

/* 用户中心按钮 + 下拉菜单 */
.user-center {
  position: relative;
}

.center-btn {
  background: none;
  border: 1px solid #d9d9d9;
  color: #555;
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
}

.center-btn:hover {
  background: #f0f7ff;
  border-color: #a8ccf0;
  color: #4a90d9;
}

.center-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  padding: 6px;
  min-width: 140px;
  z-index: 200;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.center-item {
  background: none;
  border: none;
  text-align: left;
  font-size: 14px;
  color: #333;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
}

.center-item:hover {
  background: #f0f7ff;
}

.center-item.danger {
  color: #ff4d4f;
}

.center-item.danger:hover {
  background: #fff2f0;
}

/* 音效开关 */
.sound-toggle {
  background: none;
  border: 1px solid #d9d9d9;
  color: #555;
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
}

.sound-toggle:hover {
  background: #f5f5f5;
}

.sound-toggle.off {
  color: #999;
  border-color: #e8e8e8;
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
  margin: 0 0 10px;
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

.update-more {
  margin: 0 0 16px;
  font-size: 12px;
  color: #999;
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
