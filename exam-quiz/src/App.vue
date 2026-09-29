<template>
  <div id="app">
    <!-- 顶部用户栏（只在首页显示） -->
    <div class="user-bar" v-if="userPhone && isHomePage">
      <span class="user-phone">👤 {{ userPhone }}</span>
      <button class="logout-btn" @click="logout">退出登录</button>
    </div>

    <router-view />
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
</style>
