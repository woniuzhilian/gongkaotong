import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import 'katex/dist/katex.min.css'
import './style.css'
import { getCurrentUser } from './utils/supabase'
import { syncFromCloud } from './utils/storage'

// 路由配置
const routes = [
  { path: '/auth', component: () => import('./views/AuthView.vue'), meta: { public: true } },
  { path: '/', component: () => import('./views/HomeView.vue') },
  { path: '/quiz', component: () => import('./views/QuizView.vue') },
  { path: '/wrongbook', component: () => import('./views/WrongBookView.vue') },
  { path: '/favorites', component: () => import('./views/FavoritesView.vue') },
  { path: '/result', component: () => import('./views/ResultView.vue') }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 应用启动：检查登录状态，同步云端数据
let authReady = false
let isLoggedIn = false

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

// 路由守卫：未登录跳转到 /auth
router.beforeEach(async (to) => {
  // 等待初始化完成
  if (!authReady) {
    await initAuth()
  }
  if (!to.meta.public && !isLoggedIn) {
    return { path: '/auth' }
  }
  // 已登录访问登录页，直接进首页
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
}

const app = createApp(App)
app.use(router)
app.mount('#app')
