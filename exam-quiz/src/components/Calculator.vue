<template>
  <!-- 计算器浮窗：层级在草稿纸（z 3000）之上，草稿打开时也可正常使用 -->
  <div
    v-show="visible"
    ref="panelEl"
    class="calc-float"
    :class="{ open: visible, peeking: peekZero }"
    :style="panelStyle"
    @pointerdown.stop
    @touchstart.stop
    @touchmove.stop
  >
    <!-- 标题栏：按住可拖动位置 -->
    <div class="calc-titlebar" @pointerdown="startDrag">
      <span class="calc-grip"></span>
      <span class="calc-name">🧮 计算器</span>
      <button class="calc-close" title="关闭计算器" @click.stop="$emit('close')">×</button>
    </div>

    <!-- 显示区：算式（带闪烁光标，方程等号为绿色；^ 后内容渲染为上标，5^2 → 5²）-->
    <div class="calc-display">
      <div class="calc-expr" ref="exprEl">
        <template v-for="it in renderItems" :key="it.key">
          <span v-if="it.type === 'caret'" class="calc-caret"></span>
          <span v-else-if="it.sup" class="calc-sup">{{ it.ch }}</span>
          <span v-else :class="{ 'eq-mark': it.eq, 'x-mark': it.isX }">{{ it.ch }}</span>
        </template>
        <span v-if="cursor >= expr.length" class="calc-caret"></span>
        <span v-if="!expr" class="calc-ph">输入算式或方程</span>
      </div>
      <div class="calc-res">{{ result }}</div>
    </div>

    <!-- 键盘：7 排 × 5 列；输入含 x 的等式（Eq.= 输入等号）后按 SOLVE 即可求根 -->
    <div class="calc-keys">
      <button
        v-for="(k, i) in keys"
        :key="i"
        class="calc-key"
        :class="{
          fn: k.fn, op: k.op, pi: k.pi, xx: k.xx, sq: k.sq, eq: k.eq,
          solve: k.solve, eqin: k.eqIn, cursor: k.move,
          util: k.ac || k.del || k.ans
        }"
        @pointerdown="press(k)"
        @pointerup.prevent
        @click.prevent
      >{{ k.t }}</button>
    </div>
    <div class="calc-tip-row">
      <button
        class="op-label calc-hide-btn"
        :class="{ pressed: peekZero }"
        title="按住隐藏计算器，松手恢复"
        @pointerdown="startPeek"
        @contextmenu.prevent
      >🙈 隐藏</button>
      <button class="calc-help-btn" @click="helpOpen = true">📖 使用说明</button>
    </div>

    <!-- 右下角缩放手柄 -->
    <div class="calc-resize" @pointerdown="startResize"></div>

    <!-- 使用说明弹窗 -->
    <div v-if="helpOpen" class="calc-help-mask" @click.self="helpOpen = false">
      <div class="calc-help-dialog">
        <div class="calc-help-title">计算器使用说明</div>
        <div class="calc-help-body">
          <p><b>基本运算</b>：<span class="hl">+ − × ÷</span> 加减乘除，输入算式后按 <span class="hl">=</span> 求值</p>
          <p><b>三角函数</b>：<span class="hl">sin cos tan</span> 按角度制计算（sin 30° = 0.5），按完函数自动补左括号 <span class="hl">(</span>，算完记得补 <span class="hl">)</span></p>
          <p><b>幂运算</b>：按 <span class="hl">xⁿ</span> 再输入指数，如 <span class="hl">2 xⁿ 3 =</span> 得 8；或按 <span class="hl">x²</span> 快速平方</p>
          <p><b>开方</b>：<span class="hl">√</span> 后输入被开方数，如 <span class="hl">√ 9 =</span> 得 3</p>
          <p><b>对数</b>：<span class="hl">log</span> 常用对数（以 10 为底）；<span class="hl">ln</span> 自然对数（以 e 为底）</p>
          <p><b>π 和 𝑥</b>：<span class="hl">π</span> 插入圆周率；<span class="hl">𝑥</span> 插入变量 𝑥（解方程时使用）</p>
          <p><b>Ans 键</b>：调取上一次计算结果，如刚算出 5，按 <span class="hl">Ans + 3 =</span> 得 8</p>
          <p><b>光标编辑</b>：<span class="hl">← →</span> 移动光标，<span class="hl">DEL</span> 删光标前一位，数字和函数插入到光标处</p>
          <p><b>解方程</b>：<span class="hl">Eq.=</span> 输入等号（绿色显示），如 <span class="hl">x Eq.= 2</span>，再按 <span class="hl">SOLVE</span> 得 <span class="hl">x = 2</span></p>
          <p><b>清空</b>：<span class="hl">AC</span> 全清；刚算完一道题按运算符会用上一次结果继续算</p>
          <p><b>隐藏计算器</b>：<b>按住「🙈 隐藏」按钮</b>临时隐藏整个计算器（底层做题页面完全露出），松手恢复原位，不影响计算结果</p>
        </div>
        <button class="calc-help-close" @click="helpOpen = false">知道了</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { getCalculatorSettings, setCalculatorSettings } from '../utils/storage'

const props = defineProps({
  visible: { type: Boolean, default: false },
  // 题目标识：变化时清空计算数据（每道题独立）
  questionKey: { type: [String, Number], default: '' }
})

defineEmits(['close'])

const panelEl = ref(null)
const exprEl = ref(null)

// ===== 偏好设置：透明度 / 宽度 / 位置（比例存储，云同步） =====
const saved = getCalculatorSettings()
const opacity = ref(saved.opacity)
const width = ref(saved.width)
const rx = ref(saved.x)   // 左上角位置占视口宽高的比例
const ry = ref(saved.y)

// 视口尺寸变化时让位置重新计算
const vpTick = ref(0)
function onVpResize() { vpTick.value++ }
window.addEventListener('resize', onVpResize)

let saveTimer = null
let pendingPatch = {}
function saveSettings(patch) {
  pendingPatch = { ...pendingPatch, ...patch }
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    setCalculatorSettings(pendingPatch)
    pendingPatch = {}
  }, 400)
}

const leftPx = computed(() => {
  vpTick.value
  const vw = window.innerWidth || 375
  const maxLeft = Math.max(4, vw - width.value - 4)
  return Math.min(Math.max(4, rx.value * vw), maxLeft)
})
const topPx = computed(() => {
  vpTick.value
  const vh = window.innerHeight || 667
  return Math.min(Math.max(4, ry.value * vh), Math.max(4, vh - 90))
})
// 按住「透明度」按钮：临时把计算器透明度降到 0（看清下层题目），松手恢复原设定
const peekZero = ref(false)

// 字体/间距缩放因子：以基准宽度 320px 为 1，越大越放大
const BASE_WIDTH = 320
const calcScale = computed(() => Math.max(0.75, Math.min(2.0, width.value / BASE_WIDTH)))

const panelStyle = computed(() => ({
  width: width.value + 'px',
  left: leftPx.value + 'px',
  top: topPx.value + 'px',
  '--calc-alpha': String(peekZero.value ? 0 : 1),
  '--calc-scale': calcScale.value.toFixed(3)
}))

function onOpacity(e) {
  opacity.value = Number(e.target.value) / 100
  saveSettings({ opacity: opacity.value })
}

// 按住「透明度」按钮 → 0%；松开（无论手指在哪松开）→ 恢复原设定
function startPeek(e) {
  e.preventDefault()
  peekZero.value = true
  window.addEventListener('pointerup', endPeek)
  window.addEventListener('pointercancel', endPeek)
}
function endPeek() {
  peekZero.value = false
  window.removeEventListener('pointerup', endPeek)
  window.removeEventListener('pointercancel', endPeek)
}

// ===== 拖动 =====
let dragState = null
function startDrag(e) {
  if (e.target.closest('.calc-close')) return
  e.preventDefault()
  dragState = { id: e.pointerId, sx: e.clientX, sy: e.clientY, ox: leftPx.value, oy: topPx.value }
  window.addEventListener('pointermove', onDragMove)
  window.addEventListener('pointerup', endDrag)
  window.addEventListener('pointercancel', endDrag)
}
function onDragMove(e) {
  if (!dragState || e.pointerId !== dragState.id) return
  rx.value = (dragState.ox + e.clientX - dragState.sx) / (window.innerWidth || 1)
  ry.value = (dragState.oy + e.clientY - dragState.sy) / (window.innerHeight || 1)
}
function endDrag(e) {
  if (dragState && e.pointerId === dragState.id) {
    saveSettings({ x: rx.value, y: ry.value })
    dragState = null
  }
  window.removeEventListener('pointermove', onDragMove)
  window.removeEventListener('pointerup', endDrag)
  window.removeEventListener('pointercancel', endDrag)
}

// ===== 缩放（右下角手柄，只拉宽度，高度由内容随 scale 自动匹配）=====
const MIN_W = 260
let rsState = null
function startResize(e) {
  e.preventDefault()
  e.stopPropagation()
  rsState = { id: e.pointerId, sx: e.clientX, w: width.value }
  window.addEventListener('pointermove', onResizeMove)
  window.addEventListener('pointerup', endResize)
  window.addEventListener('pointercancel', endResize)
}
function onResizeMove(e) {
  if (!rsState || e.pointerId !== rsState.id) return
  const maxW = Math.max(MIN_W, (window.innerWidth || 800) - 16)
  width.value = Math.min(Math.max(MIN_W, rsState.w + e.clientX - rsState.sx), maxW)
}
function endResize(e) {
  if (rsState && e.pointerId === rsState.id) {
    saveSettings({ width: width.value })
    rsState = null
  }
  window.removeEventListener('pointermove', onResizeMove)
  window.removeEventListener('pointerup', endResize)
  window.removeEventListener('pointercancel', endResize)
}

// ===== 计算数据（每道题独立，切题清空） =====
const expr = ref('')
const cursor = ref(0)          // 光标位置（0 ~ expr.length）
const result = ref('0')
const ans = ref(NaN)           // 上一次运算/求解结果（Ans 键调取）
const justEvaluated = ref(false) // 刚按过 = / SOLVE：再输入数字则开新式子
let lastPressAt = 0             // 按键防重入：pointerdown 快速连按时防双触发
const helpOpen = ref(false)     // 使用说明弹窗
// 把算式拆成"显示项"：^ 后有幂内容则隐藏 ^、幂用上标渲染（5^2 → 5²）；
// ^ 后没内容时单独显示 ^，让用户知道按到了
const renderItems = computed(() => {
  const s = expr.value
  const cur = cursor.value
  const items = []
  let i = 0
  while (i < s.length) {
    if (s[i] === '^') {
      if (cur === i) items.push({ key: 'c', type: 'caret' })
      const caretIdx = i
      i++
      const start = i
      if (s[i] === '(') {
        let depth = 0
        while (i < s.length) {
          const ch = s[i]
          if (ch === '(') depth++
          else if (ch === ')') { depth--; if (depth === 0) { i++; break } }
          i++
        }
      } else {
        while (i < s.length && /[0-9xπ.]/.test(s[i])) i++
      }
      if (i > start) {
        // 有幂内容 → 隐藏 ^，幂用上标渲染
        for (let k = start; k < i; k++) {
          if (k === cur) items.push({ key: 'c', type: 'caret' })
          items.push({ key: k, type: 'char', sup: true, ch: s[k] })
        }
      } else {
        // ^ 后无幂内容 → 显示 ^ 本身，让用户知道按到了
        items.push({ key: caretIdx, type: 'char', sup: false, ch: '^' })
      }
      continue
    }
    if (i === cur) items.push({ key: 'c', type: 'caret' })
    const ch = s[i]
    items.push({ key: i, type: 'char', sup: false, ch, eq: ch === '=', isX: ch === 'x' || ch === '\u{1D465}' })
    i++
  }
  if (cur >= s.length) items.push({ key: 'c', type: 'caret' })
  return items
})

watch(() => props.questionKey, resetAll)

function resetAll() {
  expr.value = ''
  cursor.value = 0
  result.value = '0'
  ans.value = NaN
  justEvaluated.value = false
}

// 光标跟随：算式行自动滚动到能看见光标的位置
async function keepCursorInView() {
  await nextTick()
  const el = exprEl.value
  const caret = el && el.querySelector('.calc-caret')
  if (!el || !caret) return
  const left = caret.offsetLeft
  if (left < el.scrollLeft) el.scrollLeft = left
  else if (left > el.scrollLeft + el.clientWidth - 10) el.scrollLeft = left - el.clientWidth + 10
}

// ===== 编辑（插入到光标处 / 删除 / 移动光标）=====
function insertAtCursor(text) {
  expr.value = expr.value.slice(0, cursor.value) + text + expr.value.slice(cursor.value)
  cursor.value += text.length
  keepCursorInView()
}

function moveCursor(d) {
  cursor.value = Math.min(Math.max(0, cursor.value + d), expr.value.length)
  keepCursorInView()
}

function backspace() {
  if (justEvaluated.value) { resetAll(); return }
  if (cursor.value <= 0) return
  expr.value = expr.value.slice(0, cursor.value - 1) + expr.value.slice(cursor.value)
  cursor.value--
  keepCursorInView()
}

// 表达式求值
// 显示串（× ÷ − π √ x sin...）→ JS 串
// 隐式乘号：值结尾（数字/)/π/x）后面跟「函数、变量、π、(」时补 *；
// 数字与数字（含小数点）之间不补，避免 30 被拆成 3*0
function insertImplicitMul(s) {
  let out = ''
  for (let i = 0; i < s.length; i++) {
    const c = s[i]
    const prev = out[out.length - 1]
    if (prev) {
      const prevEnd = /[0-9.)]/.test(prev) || prev === 'π' || prev === 'x'
      const prevNum = /[0-9.]/.test(prev)
      const curStart = /[a-z√]/.test(c) || c === 'π' || c === 'x' || c === '(' || /[0-9.]/.test(c)
      if (prevEnd && curStart && !(prevNum && /[0-9.]/.test(c))) out += '*'
    }
    out += c
  }
  return out
}

const FN = { sin: 'sind', cos: 'cosd', tan: 'tand', log: 'lg', ln: 'ln', '√': 'sqrt' }

function toJs(s) {
  let t = insertImplicitMul(s)
  t = t.replace(/×/g, '*').replace(/÷/g, '/').replace(/−/g, '-').replace(/\^/g, '**')
  t = t.replace(/(sin|cos|tan|log|ln|√)/g, (m) => FN[m])
  // 替换所有形式的 x：普通 x / 数学斜体 𝑥 (U+1D465) / 数学粗体 𝐱 等 → 统一为 X
  t = t.replace(/π/g, 'PI')
  t = t.replace(/x|\u{1D465}|\u{1D44F}|\u{1D439}/gu, 'X')
  return t
}

// 三角函数按角度制（sin(30)=0.5，符合考试习惯）
const HELPERS = {
  PI: Math.PI,
  sind: (d) => Math.sin((d * Math.PI) / 180),
  cosd: (d) => Math.cos((d * Math.PI) / 180),
  tand: (d) => Math.tan((d * Math.PI) / 180),
  lg: (x) => Math.log10(x),
  ln: (x) => Math.log(x),
  sqrt: (x) => Math.sqrt(x)
}

function evalJs(js, Xv) {
  const f = new Function('X', 'PI', 'sind', 'cosd', 'tand', 'lg', 'ln', 'sqrt', 'return (' + js + ')')
  return f(Xv, HELPERS.PI, HELPERS.sind, HELPERS.cosd, HELPERS.tand, HELPERS.lg, HELPERS.ln, HELPERS.sqrt)
}

function fmt(v) {
  if (typeof v !== 'number' || isNaN(v) || !isFinite(v)) return '无定义'
  return String(Math.round(v * 1e8) / 1e8)
}

// ===== 界面键盘：7 排 × 5 列（SOLVE / Eq.= / x / ← / → / x² 为新增键） =====
const keys = [
  { t: 'SOLVE', solve: 1 }, { t: 'Eq.=', eqIn: 1 }, { t: 'x', xx: 1 }, { t: '←', move: -1 }, { t: '→', move: 1 },
  { t: 'sin', fn: 1, ins: 'sin(' }, { t: 'cos', fn: 1, ins: 'cos(' }, { t: 'tan', fn: 1, ins: 'tan(' }, { t: '(', op: 1 }, { t: ')', op: 1 },
  { t: 'log', fn: 1, ins: 'log(' }, { t: 'ln', fn: 1, ins: 'ln(' }, { t: '√', fn: 1, ins: '√(' }, { t: 'x²', sq: 1 }, { t: 'xⁿ', op: 1, ins: '^' },
  { t: '7' }, { t: '8' }, { t: '9' }, { t: '÷', op: 1 }, { t: 'π', pi: 1 },
  { t: '4' }, { t: '5' }, { t: '6' }, { t: '×', op: 1 }, { t: 'AC', ac: 1 },
  { t: '1' }, { t: '2' }, { t: '3' }, { t: '−', op: 1 }, { t: 'DEL', del: 1 },
  { t: '0' }, { t: '.' }, { t: 'Ans', ans: 1 }, { t: '+', op: 1 }, { t: '=', eq: 1 }
]

// 按 = / SOLVE 之后的输入行为（卡西欧习惯）：
// 运算符 → 以上次结果（Ans）继续；数字/函数/π/x/Ans → 清空旧式子开新算式
function applyAfterEval(isOp) {
  if (!justEvaluated.value) return
  justEvaluated.value = false
  expr.value = isOp && isFinite(ans.value) ? fmt(ans.value) : ''
  cursor.value = expr.value.length
}

function press(k) {
  // 防重入：pointerdown 在某些设备上可能被同时派发多次（touch+pen），
  // 或 iOS Safari 快速连按时 pointerdown + click 都触发
  const now = Date.now()
  if (now - lastPressAt < 60) return   // 60ms 内同一按键只触发一次
  lastPressAt = now
  if (k.ac) { resetAll(); keepCursorInView(); return }
  if (k.del) { backspace(); return }
  if (k.eq) { doEval(); return }
  if (k.solve) { doSolve(); return }
  if (k.move) { moveCursor(k.move); return }
  applyAfterEval(!!k.op)
  if (k.eqIn) { insertAtCursor('='); return }
  if (k.sq) { insertAtCursor('^2'); return }
  if (k.ans) { insertAtCursor(isFinite(ans.value) ? fmt(ans.value) : '0'); return }
  insertAtCursor(k.ins || k.t)
}

// 自动补齐缺失的右括号（√ / sin 等函数键自带左括号，用户常漏右括号）
function autoCloseParens() {
  const e = expr.value
  const open = (e.match(/\(/g) || []).length
  const close = (e.match(/\)/g) || []).length
  if (open > close) {
    expr.value = e + ')'.repeat(open - close)
    cursor.value = expr.value.length
    keepCursorInView()
  }
}

// = 键：普通算式求值；输入里带等号（Eq.= 输入的绿色 =）时按方程求解
function doEval() {
  if (!expr.value) { result.value = '0'; return }
  autoCloseParens()
  const e = expr.value
  if (e.includes('=')) { solveEquation(e); return }
  try {
    const v = evalJs(toJs(e), NaN)
    if (typeof v !== 'number' || isNaN(v)) { result.value = '格式错误'; return }
    result.value = fmt(v)
    if (isFinite(v)) ans.value = v
    justEvaluated.value = true
  } catch (err) {
    result.value = '格式错误'
  }
}

// SOLVE 键：只有输入了等式（含 =）才作为方程求解
function doSolve() {
  if (!expr.value.includes('=')) { result.value = '请先用 Eq.= 输入等式'; return }
  autoCloseParens()
  solveEquation(expr.value)
}

// ===== 牛顿法解方程（如 x^3-x-1=0，多初值种子依次尝试，任一收敛即输出） =====
function solveEquation(raw) {
  const eqIdx = raw.indexOf('=')
  const lhs = raw.slice(0, eqIdx)
  const rhs = raw.slice(eqIdx + 1)
  // 不含未知数：只判断等式是否成立
  if (!lhs.includes('x') && !rhs.includes('x')) {
    try {
      const l = evalJs(toJs(lhs), NaN)
      const r = evalJs(toJs(rhs), NaN)
      result.value = isFinite(l) && isFinite(r) && Math.abs(l - r) < 1e-9 ? '等式成立' : '等式不成立'
    } catch (err) {
      result.value = '格式错误'
    }
    return
  }
  const js = toJs('(' + lhs + ')-(' + rhs + ')')
  let f
  try {
    f = (X) => evalJs(js, X)
    f(1) // 先验证语法
  } catch (err) {
    result.value = '格式错误'
    return
  }
  const seeds = [1, -1, 0.5, 2, 5, -5, 0.1, 10, -10, -0.5]
  for (const s of seeds) {
    let x = s
    const h = 1e-6
    let failed = false
    for (let i = 1; i <= 60; i++) {
      let fx, dfx
      try {
        fx = f(x)
        dfx = (f(x + h) - f(x - h)) / (2 * h)
      } catch (err) { failed = true; break }
      if (!isFinite(fx)) { failed = true; break }
      if (Math.abs(fx) < 1e-9) { finishSolve(x); return }
      if (!isFinite(dfx) || Math.abs(dfx) < 1e-12) { failed = true; break }
      const nx = x - fx / dfx
      if (!isFinite(nx)) { failed = true; break }
      if (Math.abs(nx - x) < 1e-10 * (1 + Math.abs(nx))) { finishSolve(nx); return }
      x = nx
    }
    if (!failed) continue
  }
  result.value = '未找到解，请检查方程'
}

function finishSolve(x) {
  const v = Math.round(x * 1e8) / 1e8
  result.value = 'x ≈ ' + fmt(v)
  ans.value = v
  justEvaluated.value = true
}

// ===== 电脑端键盘输入：打开计算器后可直接用键盘敲算式 =====
const KEY_MAP = {
  '+': { t: '+', op: 1 },
  '-': { t: '−', op: 1 },
  '*': { t: '×', op: 1 },
  '/': { t: '÷', op: 1 },
  '^': { t: '^', op: 1 },
  '(': { t: '(' },
  ')': { t: ')' },
  '.': { t: '.' }
}

function onKeyInput(e) {
  if (!props.visible) return
  const t = e.target
  // 正在其它输入框（如透明度滑杆）里操作时不接管按键
  if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return
  const k = e.key
  if (/^[0-9]$/.test(k)) { press({ t: k }); e.preventDefault(); return }
  const mapped = KEY_MAP[k]
  if (mapped) { press(mapped); e.preventDefault(); return }
  if (k === 'x' || k === 'X') { press({ t: 'x', xx: 1 }); e.preventDefault(); return }
  if (k === '=' || k === 'Enter') { press({ t: '=', eq: 1 }); e.preventDefault(); return }
  if (k === 'Backspace' || k === 'Delete') { press({ t: 'DEL', del: 1 }); e.preventDefault(); return }
  if (k === 'Escape') { press({ t: 'AC', ac: 1 }); e.preventDefault(); return }
  if (k === 'ArrowLeft') { press({ t: '←', move: -1 }); e.preventDefault(); return }
  if (k === 'ArrowRight') { press({ t: '→', move: 1 }); e.preventDefault(); return }
}

onMounted(() => {
  window.addEventListener('keydown', onKeyInput)
})

// 计算器打开时给 body 挂 calc-open 类：屏蔽底层做题页面的所有按钮
// （防止使用计算器时不小心按到下层翻页/提交等按钮）
watch(() => props.visible, (v) => {
  document.body.classList.toggle('calc-open', v)
})

onUnmounted(() => {
  window.removeEventListener('resize', onVpResize)
  window.removeEventListener('keydown', onKeyInput)
  document.body.classList.remove('calc-open')   // 兜底：卸载时确保移除
  if (saveTimer) clearTimeout(saveTimer)
  endPeek()   // 兜底：卸载时移除可能在监听中的松手事件
})
</script>

<style scoped>
/* 浮窗本体：透明度（--calc-alpha）作用于面板底色/边框/阴影，并连同按键、
   显示框等一起淡出（见下方共享规则）；调到 0 时顶部标题行与底部透明度
   滑杆行仍可见，其余不可见；不加模糊 */
.calc-float {
  position: fixed;
  z-index: 3100;
  background: rgba(255, 255, 255, var(--calc-alpha, 0.5));
  border: 1px solid rgba(0, 0, 0, calc(var(--calc-alpha, 0.5) * 0.15));
  border-radius: 12px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, calc(var(--calc-alpha, 0.5) * 0.18));
  padding: calc(8px * var(--calc-scale, 1)) calc(10px * var(--calc-scale, 1)) calc(10px * var(--calc-scale, 1));
  user-select: none;
  -webkit-user-select: none;
  touch-action: none;
  min-width: 260px;
}

/* 随透明度一起淡出的部分：显示框（算式与结果）、键盘（数字字母）、提示语、缩放手柄；
   透明度为 0 时它们全部不可见（仍可操作）。顶部标题行与底部透明度滑杆行始终可见，
   保证调到 0% 后仍能找到拖动条调回来 */
.calc-display,
.calc-keys,
.calc-tip-row,
.calc-resize {
  opacity: var(--calc-alpha, 0.5);
}

/* 按住「隐藏」按钮期间（.peeking）：整个计算器面板淡出 */
.calc-float.peeking {
  opacity: 0;
  transition: opacity 0.08s;
}
.calc-float:not(.peeking) {
  transition: opacity 0.12s;
}

.calc-titlebar {
  display: flex;
  align-items: center;
  gap: calc(8px * var(--calc-scale, 1));
  cursor: grab;
  touch-action: none;
  padding: 2px 0 calc(6px * var(--calc-scale, 1));
  flex-shrink: 0;
}

.calc-grip {
  width: calc(26px * var(--calc-scale, 1));
  height: calc(10px * var(--calc-scale, 1));
  border-radius: calc(5px * var(--calc-scale, 1));
  background: rgba(0, 0, 0, 0.12);
  position: relative;
  flex-shrink: 0;
}
.calc-grip::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: calc(12px * var(--calc-scale, 1));
  height: calc(2px * var(--calc-scale, 1));
  border-radius: calc(2px * var(--calc-scale, 1));
  background: rgba(0, 0, 0, 0.35);
}

.calc-name {
  font-size: calc(13px * var(--calc-scale, 1));
  font-weight: 600;
  color: #333;
}

.calc-close {
  margin-left: auto;
  width: calc(24px * var(--calc-scale, 1));
  height: calc(24px * var(--calc-scale, 1));
  border: none;
  border-radius: calc(6px * var(--calc-scale, 1));
  background: rgba(0, 0, 0, 0.08);
  color: #555;
  font-size: calc(16px * var(--calc-scale, 1));
  line-height: 1;
  cursor: pointer;
  flex-shrink: 0;
}
.calc-close:hover {
  background: rgba(0, 0, 0, 0.18);
}

.calc-display {
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  padding: calc(6px * var(--calc-scale, 1)) calc(8px * var(--calc-scale, 1));
  text-align: right;
  overflow: hidden;
  flex-shrink: 0;
}
.calc-expr {
  font-size: calc(12px * var(--calc-scale, 1));
  color: #666;
  min-height: calc(18px * var(--calc-scale, 1));
  line-height: calc(16px * var(--calc-scale, 1));
  white-space: nowrap;
  overflow: hidden;
  text-align: left;
  font-family: ui-monospace, Menlo, Consolas, monospace;
}
/* 方程等号：绿色，区别于普通运算 */
.eq-mark {
  color: #12a150;
  font-weight: 700;
}
/* x 变量标记：斜体 → 和正体乘号 × 视觉区分 */
.x-mark {
  font-style: italic;
  color: #0a6b3d;
  font-weight: 600;
}
/* 幂上标：^ 后内容以缩小上移的字体显示（5^2 → 5²） */
.calc-sup {
  font-size: 0.72em;
  vertical-align: super;
  line-height: 1;
}
/* 闪烁光标 */
.calc-caret {
  display: inline-block;
  width: 1px;
  height: calc(13px * var(--calc-scale, 1));
  background: #4a90d9;
  vertical-align: -2px;
  animation: calcBlink 1s step-end infinite;
}
@keyframes calcBlink {
  50% { opacity: 0; }
}
.calc-ph {
  color: #b0b0b0;
  font-size: calc(11px * var(--calc-scale, 1));
}
.calc-res {
  font-size: calc(20px * var(--calc-scale, 1));
  font-weight: 700;
  color: #222;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: ui-monospace, Menlo, Consolas, monospace;
}

.calc-keys {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: calc(5px * var(--calc-scale, 1));
  margin-top: calc(8px * var(--calc-scale, 1));
}
.calc-key {
  height: calc(32px * var(--calc-scale, 1));
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.75);
  color: #222;
  font-size: calc(14px * var(--calc-scale, 1));
  font-family: ui-monospace, Menlo, Consolas, monospace;
  cursor: pointer;
  padding: 0;
  touch-action: none;           /* 彻底禁止浏览器手势（scroll/pan/zoom）干扰按键事件 */
  -webkit-tap-highlight-color: transparent;
  transition: transform 0.05s;
}
.calc-key:active {
  background: #d8e9ff;
  transform: scale(0.94);      /* 按下即时视觉反馈，让用户知道按到了 */
}
.calc-key.fn {
  font-size: calc(12px * var(--calc-scale, 1));
  color: #4a6a8a;
}
.calc-key.op {
  color: #4a6a8a;
}
.calc-key.pi {
  color: #b25000;
  font-weight: 700;
}
.calc-key.xx {
  color: #0a6b3d;
  background: rgba(15, 220, 120, 0.14);
  font-weight: 700;
  font-style: italic;  /* 斜体 x → 和正体乘号 × 视觉区分 */
}
.calc-key.sq {
  color: #4a6a8a;
  font-size: calc(12px * var(--calc-scale, 1));
}
.calc-key.util {
  color: #a04040;
  font-size: calc(12px * var(--calc-scale, 1));
}
/* 光标键 */
.calc-key.cursor {
  font-size: calc(15px * var(--calc-scale, 1));
  color: #4a6a8a;
}
/* Eq.=：绿色文字，用于在等式中输入等号 */
.calc-key.eqin {
  color: #12a150;
  font-weight: 700;
  font-size: calc(12px * var(--calc-scale, 1));
}
/* SOLVE：方程求解键 */
.calc-key.solve {
  color: #0a6b3d;
  background: rgba(15, 220, 120, 0.14);
  font-weight: 700;
  font-size: calc(11px * var(--calc-scale, 1));
}
.calc-key.eq {
  background: #4a90d9;
  border-color: #4a90d9;
  color: #fff;
  font-weight: 700;
}
.calc-key.eq:active {
  background: #357abd;
}

.calc-tip-row {
  margin-top: calc(5px * var(--calc-scale, 1));
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: calc(8px * var(--calc-scale, 1));
  flex-shrink: 0;
}
.calc-help-btn,
.calc-hide-btn {
  font-size: calc(12px * var(--calc-scale, 1));
  padding: calc(3px * var(--calc-scale, 1)) calc(10px * var(--calc-scale, 1));
  border: 1px solid #d0d0d0;
  border-radius: calc(4px * var(--calc-scale, 1));
  background: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  font-family: inherit;
}
.calc-help-btn { color: #4a90d9; }
.calc-hide-btn { color: #888; }
.calc-help-btn:active { background: #e6f2ff; }
.calc-hide-btn:active { background: #f0f0f0; }
.calc-hide-btn.pressed { background: #ffe0e0; color: #c04040; }

/* 使用说明弹窗 */
.calc-help-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 3200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.calc-help-dialog {
  background: #fff;
  border-radius: 12px;
  max-width: 420px;
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
}
.calc-help-title {
  font-size: 16px;
  font-weight: 600;
  padding: 16px 20px 12px;
  border-bottom: 1px solid #eee;
  color: #222;
}
.calc-help-body {
  padding: 14px 20px;
  overflow-y: auto;
  font-size: 13px;
  line-height: 1.8;
  color: #333;
}
.calc-help-body p { margin: 6px 0; }
.calc-help-body .hl {
  background: #f0f6ff;
  color: #2b6cb0;
  padding: 1px 6px;
  border-radius: 3px;
  font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 12px;
}
.calc-help-close {
  margin: 8px 20px 16px;
  padding: 8px 0;
  background: #4a90d9;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

/* 右下角缩放手柄：双向拉伸（宽+高都能调） */
.calc-resize {
  position: absolute;
  right: 3px;
  bottom: 3px;
  width: calc(18px * var(--calc-scale, 1));
  height: calc(18px * var(--calc-scale, 1));
  cursor: nwse-resize;
  touch-action: none;
  z-index: 2;
  background:
    linear-gradient(
      135deg,
      transparent 0 45%,
      #4a90d9 45% 55%,
      transparent 55% 65%,
      #4a90d9 65% 75%,
      transparent 75%
    );
  border-bottom-right-radius: 10px;
}
.calc-tip-row { flex-shrink: 0; }
</style>