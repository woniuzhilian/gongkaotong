<template>
  <div class="auth-page">
    <!-- 从解析/知识点扩展页跳转来的，左上角显示返回按钮 -->
    <div class="auth-back" v-if="showBack" @click="goBackResult">← 返回</div>

    <div class="auth-header">
      <h1>工考通·岩土</h1>
      <p class="subtitle">登录后可跨设备同步刷题进度</p>
    </div>

    <!-- 注册成功提示 -->
    <div class="auth-card" v-if="registered">
      <div class="success-box">
        <div class="success-icon">✅</div>
        <h2>注册成功</h2>
        <p>账号已创建，请登录开始刷题</p>
        <button class="primary-btn" @click="goLogin">去登录</button>
      </div>
    </div>

    <!-- 重置邮件发送成功提示 -->
    <div class="auth-card" v-else-if="resetSent">
      <div class="success-box">
        <div class="success-icon">📧</div>
        <h2>重置邮件已发送</h2>
        <p>请查收邮箱，点击邮件中的链接重置密码</p>
        <button class="primary-btn" @click="goLogin">返回登录</button>
      </div>
    </div>

    <!-- 忘记密码表单 -->
    <div class="auth-card" v-else-if="mode === 'forgot'">
      <div class="tabs">
        <button class="tab active">忘记密码</button>
      </div>

      <div class="form">
        <div class="field">
          <label>注册邮箱</label>
          <input
            v-model="email"
            type="email"
            placeholder="请输入注册时填写的邮箱"
            @keyup.enter="sendResetEmail"
          />
        </div>

        <div class="error" v-if="errorMsg">{{ errorMsg }}</div>

        <button class="primary-btn" :disabled="loading" @click="sendResetEmail">
          {{ loading ? '发送中...' : '发送重置邮件' }}
        </button>

        <p class="tip" @click="switchMode('login')">
          想起密码了？返回登录
        </p>
      </div>
    </div>

    <!-- 设置新密码页面 -->
    <div class="auth-card" v-else-if="mode === 'reset'">
      <div class="tabs">
        <button class="tab active">设置新密码</button>
      </div>

      <div class="form">
        <div class="field">
          <label>新密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入新密码（至少6位）"
            maxlength="32"
          />
        </div>

        <div class="field">
          <label>确认新密码</label>
          <input
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            maxlength="32"
            @keyup.enter="updatePassword"
          />
        </div>

        <div class="error" v-if="errorMsg">{{ errorMsg }}</div>

        <button class="primary-btn" :disabled="loading" @click="updatePassword">
          {{ loading ? '提交中...' : '确认修改' }}
        </button>
      </div>
    </div>

    <!-- 登录/注册表单 -->
    <div class="auth-card" v-else>
      <div class="tabs">
        <button
          class="tab"
          :class="{ active: mode === 'login' }"
          @click="switchMode('login')"
        >登录</button>
        <button
          class="tab"
          :class="{ active: mode === 'register' }"
          @click="switchMode('register')"
        >注册</button>
      </div>

      <div class="form">
        <div class="field">
          <label>手机号</label>
          <input
            v-model="phone"
            type="tel"
            maxlength="11"
            placeholder="请输入11位手机号"
            @input="onPhoneInput"
          />
        </div>

        <div class="field" v-if="mode === 'register'">
          <label>邮箱</label>
          <input
            v-model="email"
            type="email"
            placeholder="请输入邮箱（用于重置密码）"
            maxlength="64"
          />
        </div>

        <div class="field">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码（至少6位）"
            maxlength="32"
            @keyup.enter="submit"
          />
        </div>

        <div class="field" v-if="mode === 'register'">
          <label>确认密码</label>
          <input
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            maxlength="32"
            @keyup.enter="submit"
          />
        </div>

        <div class="error" v-if="errorMsg">{{ errorMsg }}</div>

        <button class="primary-btn" :disabled="loading" @click="submit">
          {{ loading ? '请稍候...' : (mode === 'login' ? '登 录' : '注 册') }}
        </button>

        <p class="forgot-link" v-if="mode === 'login'" @click="switchMode('forgot')">
          忘记密码？
        </p>

        <p class="tip">
          {{ mode === 'login' ? '还没有账号？点上方"注册"' : '已有账号？点上方"登录"' }}
        </p>

        <div class="divider">或</div>

        <button class="guest-btn" @click="enterGuest">
          🚶 {{ showBack ? '以游客身份继续' : '以游客身份登录' }}
        </button>
        <p class="guest-tip">游客模式仅保存在本设备，无法查看解析与知识点扩展</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { signIn, signUp, resetPassword, isValidPhone, checkOtherDeviceOnline, markMySessionOnline, supabase } from '../utils/supabase'
import { syncFromCloud, pushAllToCloud } from '../utils/storage'
import { setLoginState, setGuestState } from '../main'

const router = useRouter()
const route = useRoute()

// 当带有 from=result 参数或 sessionStorage 里有来源 URL 时，显示返回按钮
const showBack = computed(() => {
  return route.query.from === 'result' || !!sessionStorage.getItem('auth_return_to')
})

const mode = ref('login') // login | register | forgot | reset
const phone = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMsg = ref('')
const loading = ref(false)
const registered = ref(false)
const resetSent = ref(false)

function switchMode(m) {
  mode.value = m
  errorMsg.value = ''
}

function onPhoneInput(e) {
  phone.value = e.target.value.replace(/\D/g, '').slice(0, 11)
}

function goLogin() {
  registered.value = false
  resetSent.value = false
  mode.value = 'login'
  password.value = ''
  confirmPassword.value = ''
  email.value = ''
  errorMsg.value = ''
}

function goBackResult() {
  const returnTo = sessionStorage.getItem('auth_return_to')
  sessionStorage.removeItem('auth_return_to')
  if (returnTo) {
    router.replace(returnTo)
  } else {
    router.replace('/')
  }
}

function enterGuest() {
  setGuestState(true)
  const returnTo = sessionStorage.getItem('auth_return_to')
  if (returnTo) {
    sessionStorage.removeItem('auth_return_to')
    router.replace(returnTo)
  } else {
    router.replace('/')
  }
}

// 页面加载时，检查是否是从重置邮件链接跳过来的
onMounted(async () => {
  await supabase.auth.getSession()
  
  const hash = window.location.hash
  let code = null
  let type = null
  
  if (hash.includes('code=')) {
    const hashParts = hash.split('?')
    if (hashParts.length > 1) {
      const hashParams = new URLSearchParams(hashParts[1])
      code = hashParams.get('code')
      type = hashParams.get('type')
    }
  }
  
  if (code) {
    try {
      const { error } = await supabase.auth.exchangeCodeForSession(code)
      if (error) throw error
      mode.value = 'reset'
      window.history.replaceState(null, '', window.location.pathname + '#/auth')
    } catch (err) {
      errorMsg.value = '链接已失效，请重新申请重置'
      mode.value = 'login'
    }
  } else {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.user) {
      if (hash.includes('type=recovery')) {
        mode.value = 'reset'
        window.history.replaceState(null, '', window.location.pathname + '#/auth')
      }
    }
  }
})

// 更新密码
async function updatePassword() {
  errorMsg.value = ''
  if (password.value.length < 6) {
    errorMsg.value = '密码至少6位'
    return
  }
  if (password.value !== confirmPassword.value) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }
  loading.value = true
  try {
    const { error } = await supabase.auth.updateUser({
      password: password.value
    })
    if (error) throw error
    alert('密码修改成功，请重新登录')
    await supabase.auth.signOut()
    goLogin()
  } catch (err) {
    errorMsg.value = err.message || '修改失败，请重试'
  } finally {
    loading.value = false
  }
}

// 校验邮箱格式
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

// 登录成功后跳回上次退出的页面
function redirectAfterLogin() {
  const returnTo = sessionStorage.getItem('auth_return_to')
  if (returnTo) {
    sessionStorage.removeItem('auth_return_to')
    router.replace(returnTo)
    return
  }
  const lastPath = localStorage.getItem('quiz_last_path')
  if (lastPath && lastPath !== '/' && !lastPath.startsWith('/auth')) {
    router.replace(lastPath)
  } else {
    router.replace('/')
  }
}

// 发送重置密码邮件
async function sendResetEmail() {
  errorMsg.value = ''

  if (!isValidEmail(email.value)) {
    errorMsg.value = '请输入正确的邮箱地址'
    return
  }

  loading.value = true
  try {
    await resetPassword(email.value)
    resetSent.value = true
  } catch (err) {
    console.error(err)
    errorMsg.value = err.message || '发送失败，请重试'
  } finally {
    loading.value = false
  }
}

async function submit() {
  errorMsg.value = ''

  if (!isValidPhone(phone.value)) {
    errorMsg.value = '请输入正确的11位手机号'
    return
  }

  if (mode.value === 'register' && !isValidEmail(email.value)) {
    errorMsg.value = '请输入正确的邮箱地址'
    return
  }

  if (password.value.length < 6) {
    errorMsg.value = '密码至少6位'
    return
  }
  if (mode.value === 'register' && password.value !== confirmPassword.value) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  try {
    if (mode.value === 'login') {
      await signIn(phone.value, password.value)
      await markMySessionOnline()
      await syncFromCloud()
      setLoginState(true)
      redirectAfterLogin()
    } else {
      await signUp(phone.value, email.value, password.value)
      await pushAllToCloud()
      registered.value = true
    }
  } catch (err) {
    console.error(err)
    if (err.message?.includes('Invalid login credentials')) {
      errorMsg.value = '手机号或密码错误'
    } else if (err.message?.includes('User already registered')) {
      errorMsg.value = '该手机号已注册，请直接登录'
    } else if (err.message?.includes('User already exists')) {
      errorMsg.value = '该邮箱已注册，请直接登录'
    } else {
      errorMsg.value = err.message || '操作失败，请重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  max-width: 420px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 100vh;
}

/* 从做题页/解析页跳转来时，左上角显示返回按钮 */
.auth-back {
  margin-bottom: 12px;
  color: #4a90d9;
  font-size: 14px;
  cursor: pointer;
}
.auth-back:hover {
  text-decoration: underline;
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h1 {
  font-size: 24px;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  color: #888;
  font-size: 14px;
}

.auth-card {
  background: #fff;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.tabs {
  display: flex;
  margin-bottom: 24px;
  border-bottom: 2px solid #f0f0f0;
}

.tab {
  flex: 1;
  background: none;
  border: none;
  padding: 10px 0;
  font-size: 16px;
  color: #888;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}

.tab.active {
  color: #4a90d9;
  border-bottom-color: #4a90d9;
  font-weight: bold;
}

.field {
  margin-bottom: 16px;
}

.field label {
  display: block;
  font-size: 14px;
  color: #555;
  margin-bottom: 6px;
}

.field input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.field input:focus {
  border-color: #4a90d9;
}

.error {
  color: #ff4d4f;
  font-size: 13px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #fff2f0;
  border-radius: 6px;
}

.primary-btn {
  width: 100%;
  padding: 12px;
  background: #4a90d9;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.primary-btn:hover:not(:disabled) {
  background: #3a7bc8;
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.forgot-link {
  text-align: center;
  color: #4a90d9;
  font-size: 13px;
  margin-top: 16px;
  margin-bottom: 0;
  cursor: pointer;
}

.forgot-link:hover {
  text-decoration: underline;
}

.tip {
  text-align: center;
  color: #aaa;
  font-size: 13px;
  margin-top: 16px;
}

/* 分隔线 "或" */
.divider {
  position: relative;
  margin: 20px 0 12px;
  text-align: center;
  font-size: 12px;
  color: #ccc;
}
.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background: #eee;
}
.divider::before { left: 0; }
.divider::after { right: 0; }

/* 游客登录按钮 */
.guest-btn {
  width: 100%;
  padding: 12px;
  background: #f5f5f5;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.guest-btn:hover {
  background: #e6f7ff;
  color: #1890ff;
  border-color: #1890ff;
}

.guest-tip {
  text-align: center;
  color: #bbb;
  font-size: 12px;
  margin-top: 8px;
  margin-bottom: 0;
}

/* 注册成功提示 */
.success-box {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.success-box h2 {
  font-size: 20px;
  color: #333;
  margin-bottom: 8px;
}

.success-box p {
  color: #888;
  font-size: 14px;
  margin-bottom: 24px;
}
</style>
