<template>
  <div class="security-page">
    <div class="security-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h2 class="security-title">安全中心</h2>
    </div>

    <div class="security-card">
      <h3 class="card-title">修改密码</h3>

      <div class="field">
        <label>原密码</label>
        <input v-model="oldPwd" type="password" placeholder="请输入当前密码" autocomplete="current-password" />
      </div>
      <div class="field">
        <label>新密码</label>
        <input v-model="newPwd" type="password" placeholder="至少 6 位" autocomplete="new-password" />
      </div>
      <div class="field">
        <label>确认新密码</label>
        <input v-model="confirmPwd" type="password" placeholder="再次输入新密码" autocomplete="new-password" />
      </div>

      <div class="error" v-if="error">{{ error }}</div>

      <button class="submit-btn" :disabled="loading" @click="submit">
        {{ loading ? '提交中...' : '确认修改' }}
      </button>
      <div class="success" v-if="success">密码修改成功，下次登录请使用新密码</div>
    </div>

    <div class="security-card email-card">
      <h3 class="card-title">修改绑定邮箱</h3>
      <p class="card-tip">为保障账号安全，需完整输入原邮箱与密码，验证通过后方可绑定新邮箱。</p>

      <div class="field">
        <label>原邮箱</label>
        <input v-model="oldEmail" type="email" placeholder="请输入当前绑定的完整邮箱" autocomplete="email" />
      </div>
      <div class="field">
        <label>密码</label>
        <input v-model="pwd" type="password" placeholder="请输入账号密码" autocomplete="current-password" />
      </div>
      <div class="field">
        <label>新邮箱</label>
        <input v-model="newEmail" type="email" placeholder="请输入要绑定的新邮箱" autocomplete="off" />
      </div>
      <div class="field">
        <label>确认新邮箱</label>
        <input v-model="confirmEmail" type="email" placeholder="请再次输入新邮箱" autocomplete="off" />
      </div>

      <div class="error" v-if="emailError">{{ emailError }}</div>

      <button class="submit-btn" :disabled="emailLoading" @click="submitEmail">
        {{ emailLoading ? '提交中...' : '确认修改' }}
      </button>
      <div class="success" v-if="emailSuccess">绑定邮箱修改成功，重置密码邮件将发送到新邮箱</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { changePassword, changeEmail } from '../utils/supabase'

const router = useRouter()
const oldPwd = ref('')
const newPwd = ref('')
const confirmPwd = ref('')
const error = ref('')
const success = ref(false)
const loading = ref(false)

// 修改绑定邮箱
const oldEmail = ref('')
const pwd = ref('')
const newEmail = ref('')
const confirmEmail = ref('')
const emailError = ref('')
const emailSuccess = ref(false)
const emailLoading = ref(false)

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

function goBack() {
  // 用户中心入口只在首页，返回即回首页（不依赖历史栈）
  router.replace('/')
}

async function submit() {
  error.value = ''
  success.value = false
  if (!oldPwd.value) { error.value = '请输入原密码'; return }
  if (newPwd.value.length < 6) { error.value = '新密码至少 6 位'; return }
  if (newPwd.value === oldPwd.value) { error.value = '新密码不能与原密码相同'; return }
  if (newPwd.value !== confirmPwd.value) { error.value = '两次输入的新密码不一致'; return }
  loading.value = true
  try {
    await changePassword(oldPwd.value, newPwd.value)
    success.value = true
    oldPwd.value = ''
    newPwd.value = ''
    confirmPwd.value = ''
  } catch (e) {
    error.value = e.message || '修改失败，请重试'
  } finally {
    loading.value = false
  }
}

// 修改绑定邮箱
async function submitEmail() {
  emailError.value = ''
  emailSuccess.value = false

  if (!isValidEmail(oldEmail.value)) {
    emailError.value = '请输入正确的原邮箱地址'
    return
  }
  if (!pwd.value) {
    emailError.value = '请输入密码'
    return
  }
  if (!isValidEmail(newEmail.value)) {
    emailError.value = '请输入正确的新邮箱地址'
    return
  }
  if (newEmail.value !== confirmEmail.value) {
    emailError.value = '两次输入的新邮箱不一致'
    return
  }
  if (newEmail.value.toLowerCase() === oldEmail.value.toLowerCase()) {
    emailError.value = '新邮箱不能与原邮箱相同'
    return
  }

  emailLoading.value = true
  try {
    await changeEmail(oldEmail.value.trim(), pwd.value, newEmail.value.trim())
    emailSuccess.value = true
    oldEmail.value = ''
    pwd.value = ''
    newEmail.value = ''
    confirmEmail.value = ''
  } catch (e) {
    emailError.value = e.message || '修改失败，请重试'
  } finally {
    emailLoading.value = false
  }
}
</script>

<style scoped>
.security-page {
  max-width: 480px;
  margin: 0 auto;
  padding: 16px;
}

.security-header {
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

.security-title {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.security-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-title {
  margin: 0 0 16px;
  font-size: 16px;
  color: #333;
}

.card-tip {
  margin: 0 0 14px;
  font-size: 12px;
  color: #999;
  line-height: 1.6;
}

.email-card {
  margin-top: 16px;
}

.field {
  margin-bottom: 14px;
}
.field label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
}
.field input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}
.field input:focus {
  border-color: #4a90d9;
}

.error {
  color: #ff4d4f;
  font-size: 13px;
  margin-bottom: 12px;
}

.success {
  color: #52c41a;
  font-size: 13px;
  margin-top: 12px;
  text-align: center;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: #4a90d9;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
}
.submit-btn:hover:not(:disabled) {
  background: #357abd;
}
.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
