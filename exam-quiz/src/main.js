import { createApp, reactive } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import 'katex/dist/katex.min.css'
import './style.css'
import { getCurrentUser } from './utils/supabase'
import { syncFromCloud } from './utils/storage'
import { attachGlobalSoundListener } from './utils/sound'

// 路由配置
const routes = [
  { path: '/auth', component: () => import('./views/AuthView.vue'), meta: { public: true } },
  { path: '/', component: () => import('./views/HomeView.vue') },
  { path: '/quiz', component: () => import('./views/QuizView.vue') },
  { path: '/wrongbook', component: () => import('./views/WrongBookView.vue') },
  { path: '/favorites', component: () => import('./views/FavoritesView.vue') },
  { path: '/changelog', component: () => import('./views/ChangelogView.vue') },
  { path: '/security', component: () => import('./views/SecurityView.vue') },
  { path: '/result', component: () => import('./views/ResultView.vue') }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 应用启动：检查登录状态，同步云端数据
let authReady = false
let isLoggedIn = false

// 游客登录状态（用 reactive 包装，让组件可以直接响应式使用）
export const guestState = reactive({ value: false })

async function initAuth() {
  try {
    const user = await getCurrentUser()
    isLoggedIn = !!user
    // 已登录则拉取云端进度覆盖本地
    if (isLoggedIn) {
      await syncFromCloud()
    }
  } catch (e) {
    console.error('初始化登录状态失败:', e)
    isLoggedIn = false
  } finally {
    authReady = true
  }
}

// 路由守卫：未登录且非游客跳转到 /auth
router.beforeEach(async (to) => {
  // 等待初始化完成
  if (!authReady) {
    await initAuth()
  }
  if (!to.meta.public && !isLoggedIn && !guestState.value) {
    return { path: '/auth' }
  }
  // 已登录用户访问登录页，直接进首页；游客访问登录页允许（游客想转成正常用户登录）
  if (to.path === '/auth' && isLoggedIn) {
    return { path: '/' }
  }
  // 记录用户访问的页面（用于登录后跳回上次位置）
  if (!to.meta.public) {
    localStorage.setItem('quiz_last_path', to.fullPath)
  }
  return true
})

// 登录状态变化时同步更新（其他地方调用登出后会触发）
export function setLoginState(loggedIn) {
  isLoggedIn = loggedIn
  if (loggedIn) {
    guestState.value = false
    localStorage.removeItem('is_guest')
  }
}

// 游客状态管理
export function setGuestState(guest) {
  guestState.value = !!guest
  if (guest) {
    localStorage.setItem('is_guest', '1')
    isLoggedIn = false
  } else {
    localStorage.removeItem('is_guest')
  }
}

export function getIsGuest() {
  return guestState.value
}

// 应用启动时恢复游客状态
if (localStorage.getItem('is_guest') === '1') {
  guestState.value = true
}

const app = createApp(App)
app.use(router)
app.mount('#app')

// 全局音效监听（普通按钮点击音；提交按钮的正确/错误音效由 QuizView 单独触发）
attachGlobalSoundListener()
