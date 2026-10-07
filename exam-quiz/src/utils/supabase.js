// Supabase 连接封装 + 云端进度同步
import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://ejpvwumcqjfutvcycevz.supabase.co'
const SUPABASE_ANON_KEY = 'sb_publishable_GB7W1v06ek0hiMvV1aTdqA_N5cMHr0J'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// ===== 手机号 ↔ 假邮箱 转换 =====
// 把手机号拼成假邮箱，Supabase Auth 只认 email+password，
// 用户侧全程只看到手机号，不感知邮箱。
const EMAIL_DOMAIN = '@phone.quiz.local'

export function phoneToEmail(phone) {
  return `${phone}${EMAIL_DOMAIN}`
}

export function emailToPhone(email) {
  if (!email) return ''
  return email.replace(EMAIL_DOMAIN, '')
}

// 校验手机号格式（中国大陆 11 位，1 开头）
export function isValidPhone(phone) {
  return /^1[3-9]\d{9}$/.test(phone)
}

// ===== 认证 =====
// 注册：手机号 + 邮箱 + 密码
export async function signUp(phone, email, password) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { data: { phone } }
  })
  if (error) throw error
  // 关闭了邮箱确认，注册完直接有 session
  return data
}

// 登录：手机号 + 密码（先通过手机号查询邮箱，再用邮箱登录）
export async function signIn(phone, password) {
  // 先通过手机号查询对应的邮箱
  const { data: userEmail, error: queryError } = await supabase
    .rpc('get_email_by_phone', { phone_input: phone })
  
  if (queryError || !userEmail) {
    throw new Error('该手机号未注册')
  }

  const { data, error } = await supabase.auth.signInWithPassword({
    email: userEmail,
    password
  })
  if (error) throw error
  return data
}

// 忘记密码：发送重置邮件
export async function resetPassword(email) {
  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: 'https://gongkaotong.pages.dev/auth'
  })
  if (error) throw error
}

// 修改密码（安全中心）：需传入原密码做重新认证，再更新为新密码
export async function changePassword(oldPassword, newPassword) {
  // 1. 用原密码重新登录，满足 Supabase 的敏感操作重认证要求
  const user = await getCurrentUser()
  if (!user) throw new Error('请先登录')
  const { error: reErr } = await supabase.auth.signInWithPassword({
    email: user.email,
    password: oldPassword
  })
  if (reErr) throw new Error('原密码不正确')
  // 2. 更新为新密码
  const { error } = await supabase.auth.updateUser({ password: newPassword })
  if (error) {
    if (String(error.message).toLowerCase().includes('password')) throw new Error('新密码不符合要求（至少 6 位）')
    throw error
  }
}

// 修改绑定邮箱（安全中心）：需完整输入原邮箱 + 密码做重认证，通过后绑定新邮箱
export async function changeEmail(oldEmail, password, newEmail) {
  const user = await getCurrentUser()
  if (!user) throw new Error('请先登录')
  // 1. 原邮箱 + 密码重新登录，验证身份
  const { error: reErr } = await supabase.auth.signInWithPassword({
    email: oldEmail,
    password
  })
  if (reErr) throw new Error('原邮箱或密码不正确')
  // 2. 绑定新邮箱
  const { error } = await supabase.auth.updateUser({ email: newEmail })
  if (error) {
    const msg = String(error.message).toLowerCase()
    if (msg.includes('already') || msg.includes('registered')) throw new Error('该邮箱已被其他账号使用')
    if (msg.includes('confirm')) throw new Error('系统已向新邮箱发送确认邮件，请点击邮件中的链接完成绑定')
    throw error
  }
}

// 登出
export async function signOut() {
  const { error } = await supabase.auth.signOut()
  if (error) throw error
}

// 获取当前登录用户（返回 { phone, userId } 或 null）
export async function getCurrentUser() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.user) return null
  return {
    userId: session.user.id,
    phone: session.user.user_metadata?.phone || '',
    email: session.user.email,
    session
  }
}

// 监听登录状态变化
export function onAuthStateChange(callback) {
  return supabase.auth.onAuthStateChange((event, session) => {
    if (session?.user) {
      callback({
        userId: session.user.id,
        phone: session.user.user_metadata?.phone || ''
      })
    } else {
      callback(null)
    }
  })
}

// ===== 云端进度同步 =====
// 表 user_progress：id(用户UUID) / progress / answers / wrong / results / updated_at

let syncTimer = null
const SYNC_DEBOUNCE_MS = 1500

// 把本地 4 份数据推到云端（防抖）
export function scheduleCloudSync(localData) {
  if (syncTimer) clearTimeout(syncTimer)
  syncTimer = setTimeout(() => {
    pushToCloud(localData)
  }, SYNC_DEBOUNCE_MS)
}

// 立即推送（登出前/手动保存时用）
export async function pushToCloud(localData) {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.user) return
  const userId = session.user.id

  markSelfPush() // 标记本次是自己推送，实时事件里忽略

  const payload = {
    id: userId,
    progress: localData.progress || {},
    answers: localData.answers || {},
    wrong: localData.wrong || {},
    favorites: localData.favorites || {},
    results: localData.results || {},
    settings: localData.settings || {},
    updated_at: new Date().toISOString()
  }

  // upsert：存在就更新，不存在就插入
  let { error } = await supabase
    .from('user_progress')
    .upsert(payload)

  // 若数据库尚未有 settings 列，去掉该字段重试，保证其余数据同步不受影响
  if (error && String(error.message).includes('settings')) {
    const { settings, ...rest } = payload
    error = (await supabase.from('user_progress').upsert(rest)).error
  }
  // 若数据库尚未有 favorites 列，去掉该字段重试，保证其余数据同步不受影响
  if (error && String(error.message).includes('favorites')) {
    const { favorites, ...rest } = payload
    delete rest.settings
    error = (await supabase.from('user_progress').upsert(rest)).error
  }
  if (error) {
    console.error('云同步失败:', error.message)
  }
}

// 从云端拉取进度
export async function pullFromCloud() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.user) return null
  const userId = session.user.id

  let { data, error } = await supabase
    .from('user_progress')
    .select('progress, answers, wrong, favorites, results, settings, updated_at')
    .eq('id', userId)
    .single()

  // 若 settings 列尚不存在，降级为不含该字段的查询
  if (error && String(error.message).includes('settings')) {
    const r2 = await supabase
      .from('user_progress')
      .select('progress, answers, wrong, favorites, results, updated_at')
      .eq('id', userId)
      .single()
    data = r2.data
    error = r2.error
  }

  // 若 favorites 列尚不存在，降级为不含该字段的查询
  if (error && String(error.message).includes('favorites')) {
    const r3 = await supabase
      .from('user_progress')
      .select('progress, answers, wrong, results, updated_at')
      .eq('id', userId)
      .single()
    data = r3.data
    error = r3.error
  }

  if (error) {
    // PGRST116 = 没有数据（新用户），不算错误
    if (error.code !== 'PGRST116') {
      console.error('拉取云端进度失败:', error.message)
    }
    return null
  }
  return data
}

// ===== 实时同步（多设备同时在线时自动更新）=====

let progressChannel = null
// 标记本次推送是自己触发的，收到 Realtime 事件时忽略，避免循环
let isSelfPush = false

export function markSelfPush() {
  isSelfPush = true
  // 3 秒后自动解除标记（覆盖网络延迟）
  setTimeout(() => { isSelfPush = false }, 3000)
}

// 订阅当前用户的进度变化，收到更新时调用 callback
export function subscribeToProgress(userId, onRemoteUpdate) {
  // 先取消旧订阅
  unsubscribeProgress()

  progressChannel = supabase
    .channel(`progress:${userId}`)
    .on('postgres_changes', {
      event: 'UPDATE',
      schema: 'public',
      table: 'user_progress',
      filter: `id=eq.${userId}`
    }, (payload) => {
      // 自己推上去的数据，忽略
      if (isSelfPush) return
      onRemoteUpdate(payload.new)
    })
    .subscribe()
}

export function unsubscribeProgress() {
  if (progressChannel) {
    supabase.removeChannel(progressChannel)
    progressChannel = null
  }
}

// ===== 单点登录（不允许同一账号多设备同时在线）=====

let mySessionId = null

// 生成随机 session ID
export function generateSessionId() {
  return 'sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 10)
}

export function getMySessionId() {
  return mySessionId
}

// 获取设备信息（简单描述）
function getDeviceInfo() {
  const ua = navigator.userAgent
  let device = '未知设备'
  if (/Mobile/.test(ua)) device = '手机'
  else if (/iPad/.test(ua)) device = '平板'
  else device = '电脑'
  const browser = /Chrome/.test(ua) ? 'Chrome' : /Safari/.test(ua) ? 'Safari' : /Firefox/.test(ua) ? 'Firefox' : '浏览器'
  return device + '(' + browser + ')'
}

// 登录前检查：返回 { online: boolean, device: string, time: string }
export async function checkOtherDeviceOnline() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.user) return { online: false }
  const userId = session.user.id

  const { data, error } = await supabase
    .from('user_progress')
    .select('session_id, last_device, last_login_at')
    .eq('id', userId)
    .single()

  if (error || !data?.session_id) return { online: false }
  if (data.session_id === mySessionId) return { online: false }
  return {
    online: true,
    device: data.last_device || '未知设备',
    time: data.last_login_at
  }
}

// 登录成功后，把当前 session 标记为在线（覆盖旧设备）
export async function markMySessionOnline() {
  mySessionId = generateSessionId()
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.user) return
  const userId = session.user.id

  markSelfPush() // 标记本次是自己推送，实时事件里忽略

  await supabase
    .from('user_progress')
    .upsert({
      id: userId,
      session_id: mySessionId,
      last_device: getDeviceInfo(),
      last_login_at: new Date().toISOString()
    })

  return mySessionId
}

// 登出时清除 session 标记
export async function clearMySession() {
  mySessionId = null
}
// ===== 用户反馈 =====
// 提交题目反馈
export async function submitFeedback(questionId, feedbackParts, feedbackText, bigSubject) {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.user) throw new Error('请先登录')

  const { error } = await supabase
    .from('user_feedback')
    .insert({
      user_id: session.user.id,
      question_id: questionId,
      big_subject: bigSubject || null,
      feedback: JSON.stringify({
        parts: feedbackParts,
        text: feedbackText || ''
      })
    })

  if (error) throw error
}

// ===== 消息中心 =====
// 获取当前用户的消息列表（新消息在前）
export async function fetchMessages() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.user) throw new Error('请先登录')
  const { data, error } = await supabase
    .from('messages')
    .select('id, title, content, is_read, created_at')
    .eq('user_id', session.user.id)
    .order('created_at', { ascending: false })
  if (error) throw error
  return data || []
}

// 获取未读消息数量
export async function fetchUnreadCount() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.user) return 0
  const { count, error } = await supabase
    .from('messages')
    .select('id', { count: 'exact', head: true })
    .eq('user_id', session.user.id)
    .eq('is_read', false)
  if (error) return 0
  return count || 0
}

// 标记消息已读
export async function markMessageRead(messageId) {
  const { error } = await supabase
    .from('messages')
    .update({ is_read: true })
    .eq('id', messageId)
  if (error) throw error
}

// ===== 意见建议 =====
// 提交意见建议
export async function submitSuggestion(content) {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.user) throw new Error('请先登录')
  const { error } = await supabase
    .from('suggestions')
    .insert({ user_id: session.user.id, content })
  if (error) throw error
}

// 获取当前用户提交过的意见建议（新提交在前）
export async function fetchSuggestions() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.user) throw new Error('请先登录')
  const { data, error } = await supabase
    .from('suggestions')
    .select('id, content, status, created_at')
    .eq('user_id', session.user.id)
    .order('created_at', { ascending: false })
  if (error) throw error
  return data || []
}