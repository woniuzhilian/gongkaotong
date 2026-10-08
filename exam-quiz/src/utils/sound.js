// 全局音效：用 Web Audio API 程序生成，无需外部音频文件、无授权问题
// 三种音效：普通按钮点击、作答正确、作答错误

let ctx = null
let audioUnlocked = false
// 音效开关持久化：用户关掉后刷新/换设备（本地）保持关闭
let muted = false
try { muted = localStorage.getItem('exam_quiz_sound_off') === '1' } catch (e) {}

function getCtx() {
  if (typeof window === 'undefined') return null
  if (!ctx) {
    try {
      ctx = new (window.AudioContext || window.webkitAudioContext)()
    } catch (e) {
      return null
    }
  }
  return ctx
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 关闭旧 ctx 并重建（resume 失败时的兜底，避免 ctx 永久挂死导致之后所有音效失效）
function rebuildCtx() {
  try {
    if (ctx && ctx.state !== 'closed') { try { ctx.close() } catch (e) {} }
  } catch (e) {}
  ctx = null
  return getCtx()
}

// 确保 ctx 处于 running：先尝试 resume（带短暂超时），仍非 running 则关闭重建
// 返回 Promise<boolean> 表示当前是否可发声
async function ensureRunning() {
  let c = getCtx()
  if (!c) return false
  if (c.state === 'running') return true
  // suspended / interrupted：尝试恢复
  if (c.state === 'suspended') {
    try { await Promise.race([c.resume(), delay(300)]) } catch (e) {}
  }
  if (ctx && ctx.state === 'running') return true
  // resume 失败或始终非 running：关闭旧 ctx 重建，并在（可能的用户手势内）再次恢复
  rebuildCtx()
  c = ctx
  if (c && c.state === 'suspended') {
    try { await Promise.race([c.resume(), delay(300)]) } catch (e) {}
  }
  return !!(c && c.state === 'running')
}

// 手机切屏/锁屏后浏览器会挂起 AudioContext，回到前台时恢复；
// resume 失败（如 iOS 因缺少用户手势被拒绝）则重建，避免 ctx 永久挂死
if (typeof document !== 'undefined') {
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && ctx && ctx.state !== 'running') {
      ensureRunning()
    }
  })
  // 部分浏览器在 pageshow（返回缓存页）时同样处于挂起状态
  window.addEventListener('pageshow', () => {
    if (ctx && ctx.state !== 'running') ensureRunning()
  })
}

// 用户交互（点击/触摸）时解锁/恢复 AudioContext（浏览器自动播放策略要求）
export function unlockAudio() {
  const c = getCtx()
  if (!c) return
  // 统一处理：状态非 running 则尝试 resume，失败则重建；
  // 在用户手势内调用，iOS 才允许 resume，故每次 pointerdown 都调用以增强恢复机会
  if (c.state !== 'running') ensureRunning()
  audioUnlocked = true
}

// 设置静音
export function setMuted(v) {
  muted = !!v
  try { localStorage.setItem('exam_quiz_sound_off', muted ? '1' : '0') } catch (e) {}
  // 打开音效时强制恢复/重建 ctx，解决“关掉再开也没声”的问题
  if (!muted) ensureRunning()
}

export function isMuted() {
  return muted
}

// 切换音效开关，返回切换后的状态（true=已静音）
export function toggleMuted() {
  setMuted(!muted)
  // setMuted 内部已在打开音效时恢复/重建 ctx
  return muted
}

/**
 * 通用音符播放
 * @param {number[]} freqs  各音频率 (Hz)，按顺序播放
 * @param {number[]} durationsMs 各音持续时长 (ms)
 * @param {'sine'|'square'|'triangle'} type 波形
 * @param {number} volume 0~1
 */
async function playSequence(freqs, durationsMs, type = 'sine', volume = 0.2) {
  if (muted) return
  let c = getCtx()
  if (!c) return
  // 发声前先确保 AudioContext 处于 running：
  // resume 成功（或短暂超时）后再创建 oscillator；resume 失败则重建新 ctx，
  // 避免在 state 仍为 suspended 时创建无效节点、以及 ctx 永久挂死
  if (c.state !== 'running') {
    await ensureRunning()
    c = ctx // 重建后 ctx 可能已更换
    if (!c || c.state !== 'running') return
  }
  let t = c.currentTime
  const master = c.createGain()
  master.gain.value = volume
  master.connect(c.destination)

  for (let i = 0; i < freqs.length; i++) {
    const osc = c.createOscillator()
    const g = c.createGain()
    osc.type = type
    osc.frequency.setValueAtTime(freqs[i], t)
    g.gain.setValueAtTime(0, t)
    g.gain.linearRampToValueAtTime(1, t + 0.005) // 快速淡入避免爆音
    g.gain.exponentialRampToValueAtTime(0.0001, t + durationsMs[i] / 1000)
    osc.connect(g)
    g.connect(master)
    osc.start(t)
    osc.stop(t + durationsMs[i] / 1000 + 0.02)
    t += durationsMs[i] / 1000
  }
}

// 普通按钮点击：短促 click
export function playClick() {
  playSequence([880], [50], 'sine', 0.18)
}

// 作答正确：上行双音（660 → 880 Hz）
export function playCorrect() {
  playSequence([660, 880], [90, 120], 'triangle', 0.22)
}

// 作答错误：下行 buzz（440 → 220 Hz，方波更像"错误提示"）
export function playWrong() {
  playSequence([440, 220], [110, 160], 'square', 0.22)
}

/**
 * 给 window 挂一个全局 click 监听：点击任何"可交互元素"时播放普通音效
 * 覆盖 <button> 和带有 click 事件的常见卡片元素（.subject-card / .mode-card / .item-card 等）
 * 排除掉：提交按钮（由 QuizView 按正确/错误手动播放）、data-sound="none"
 */
let globalListenerAttached = false
export function attachGlobalSoundListener() {
  if (globalListenerAttached) return
  globalListenerAttached = true
  if (typeof window === 'undefined') return
  const interactiveSelector = 'button, .subject-card, .mode-card, .item-card, .big-subject-btn, .report-btn, .submit-btn, .knowledge-btn, .fav-btn, .scratch-btn, .close-btn, .tab-btn, .restart-btn, .back-btn, .home-btn, .nav-btn'

  // 每次交互都尝试解锁/恢复 ctx（切后台回来后、iOS 手势内都可能需要重新 resume）
  document.addEventListener('pointerdown', () => { unlockAudio() })

  document.addEventListener('click', (e) => {
    if (muted) return
    const target = e.target && e.target.closest ? e.target.closest(interactiveSelector) : null
    if (!target) return
    // 提交按钮（QuestionCard 的 submit-btn）的正确/错误音效由 QuizView 手动播放，此处跳过
    if (target.classList && target.classList.contains('submit-btn')) return
    // data-sound="none" 强制跳过
    if (target.dataset && target.dataset.sound === 'none') return
    playClick()
  }, true)
}
