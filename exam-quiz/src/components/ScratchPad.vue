<template>
  <!-- 用 v-show 保留同一题内的草稿（关闭再打开还在，切题才清空）；
       但 scratch-mask 类只在打开时挂上——App.vue 的滑动导航与 QuizView 的
       ←/→ 切题都靠 querySelector('.scratch-mask') 判断遮罩是否打开 -->
  <!-- touch 事件加 .stop：草稿打开时不让边缘滑动导航（document 级监听）看到任何触摸 -->
  <div
    :class="{ 'scratch-mask': visible }"
    v-show="visible"
    @touchstart="stopTouch"
    @touchmove="stopTouch"
    @touchend="stopTouch"
    @touchcancel="stopTouch"
  >
    <!-- 底层画布：已确认的笔画，同时接收全部指针事件 -->
    <canvas
      ref="canvasEl"
      class="scratch-canvas"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    ></canvas>
    <!-- 顶层画布：只画正在拖动的图形（不回填整幅位图，保证图形跟手） -->
    <canvas ref="overlayEl" class="scratch-overlay"></canvas>

    <!-- 提示语常驻，方便随时确认当前处于草稿纸模式 -->
    <div class="scratch-hint">
      {{ penAvailable ? '✍️ 已检测到手写笔：仅手写笔可书写' : '在题目上直接书写圈画' }} · 点右上角 × 退出
    </div>

    <!-- 真机诊断（默认隐藏，点工具栏「粗细」三下开关）：用于定位事件被哪个分支丢弃 -->
    <div v-if="debugOn" class="scratch-diag">
      <div>{{ diagBuild }} · {{ diag.last }}</div>
      <div>down {{ diag.down }} | commit {{ diag.commit }} | strokes {{ strokes.length }}</div>
      <div>split {{ diag.moveSplit }} | noDown {{ diag.moveNoDown }} | coalesced {{ diag.coalesced }}</div>
      <div>gapT {{ 80 }}ms | gapS {{ 50 }}px | pts avg {{ diag.avgPts }} min {{ diag.minPts }}</div>
    </div>

    <button class="scratch-close" title="退出草稿" @click="$emit('close')">×</button>

    <div class="scratch-bar">
      <div class="eraser-tip" v-if="tool === 'eraser'">
        橡皮擦：{{ eraserMode === 'object' ? '按对象擦除 · 点中哪一笔就删掉整笔' : '连续擦除 · 划过即擦掉笔迹' }}（长按图标切换）
      </div>
      <div class="bar-row">
        <button
          v-for="t in tools"
          :key="t.key"
          class="tool-btn"
          :class="{ active: tool === t.key }"
          :title="t.key === 'eraser' ? '橡皮擦（长按图标切换模式）' : t.label"
          @click="pickTool(t)"
          @pointerdown="t.key === 'eraser' ? onEraserDown() : null"
          @pointerup="t.key === 'eraser' ? onEraserUp() : null"
          @pointerleave="t.key === 'eraser' ? onEraserUp() : null"
          @pointercancel="t.key === 'eraser' ? onEraserUp() : null"
        >
          <!-- 橡皮擦用线条图标，一眼可辨 -->
          <svg
            v-if="t.key === 'eraser'"
            class="tool-svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21" />
            <path d="M22 21H7" />
            <path d="m5 11 9 9" />
          </svg>
          <template v-else>{{ t.icon }}</template>
        </button>
        <span class="bar-sep"></span>
        <button class="tool-btn" title="撤销" :disabled="strokes.length === 0" @click="undo">↶</button>
        <button class="tool-btn" title="清空" :disabled="strokes.length === 0" @click="clearAll">🗑</button>
        <span class="bar-sep"></span>
        <button class="tool-btn" title="计算器" @click="$emit('open-calculator')">🧮</button>
      </div>
      <div class="bar-row">
        <span class="bar-label" @click="tapDiag">粗细</span>
        <button
          v-for="s in sizes"
          :key="s"
          class="size-btn"
          :class="{ active: size === s }"
          :title="'画笔粗细 ' + s"
          @click="size = s"
        ><span class="size-dot" :style="{ width: (s + 5) + 'px', height: (s + 5) + 'px' }"></span></button>
        <span class="bar-sep"></span>
        <span class="bar-label">颜色</span>
        <button
          v-for="c in colors"
          :key="c"
          class="color-btn"
          :class="{ active: color === c }"
          :style="{ background: c }"
          :title="c"
          @click="color = c"
        ></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, shallowRef, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  // 题目标识：变化时自动清空草稿（切题自动清空）
  questionKey: { type: [String, Number], default: '' }
})

defineEmits(['close', 'open-calculator'])

const canvasEl = ref(null)
const overlayEl = ref(null)
const tool = ref('pen')
// object = 按对象擦除（默认，点一下删掉整笔）；stroke = 连续擦除（长按图标切换）
const eraserMode = ref('object')
const color = ref('#222222')
const size = ref(4)
const strokes = shallowRef([])   // 笔画含大量坐标点，避免深层响应式开销

const tools = [
  { key: 'pen', icon: '✏️', label: '画笔' },
  { key: 'line', icon: '╱', label: '直线' },
  { key: 'rect', icon: '▭', label: '矩形' },
  { key: 'circle', icon: '◯', label: '圆形' },
  { key: 'eraser', icon: '', label: '橡皮擦' }   // 图标用内联 SVG
]
const sizes = [2, 4, 7, 12]
const colors = ['#222222', '#e03131', '#1c7ed6', '#2f9e44', '#e8590c', '#9c36b5']

let ctx = null            // 底层画布：已确认的笔画
let octx = null           // 顶层画布：正在拖动的图形预览
let current = null        // 正在画的这一笔
let drawing = false
let erasingObject = false // 按对象擦除：按住拖动可连续删除多笔
let erasingPid = 0        // 触发按对象擦除的指针 id（只响应该指针的移动）
let lastMoveTs = 0        // 上一次 pointermove 时间戳（用于"隐式笔画切分"）
// iPadOS Safari 合并 pointerdown 事件时，我们靠"移动间隙"检测笔画边界：
// 时间间隙（ms）或空间间隙（px）任一达到就视为：上一笔结束，当前 move 是新笔起点
const STROKE_GAP_T = 80
const STROKE_GAP_S = 50
// 真机诊断（默认隐藏，点工具栏「粗细」三下开关）：统计各分支的丢弃原因，
// 用于在 iPad 上定位"移动被谁吃掉"。定位完成后可整块删除
const diagBuild = 'F2026-10-06'  // 隐式笔画切分 + pointerdown 兜底版本
const debugOn = ref(false)
const diag = reactive({
  down: 0, downBtn: 0, downTouch: 0, downNoEl: 0,
  move: 0, moveTouch: 0, moveNoCur: 0, movePid: 0,
  up: 0, upTs: 0, upPid: 0, commit: 0,
  undo: 0, clear: 0, qkChange: 0, setup: 0, strokesWatch: '-',
  avgPts: 0, minPts: 0,
  // 隐式切分计数器（pointerdown 被 Safari 跳过时的补救路径）
  moveSplit: 0,     // 移动间隙触发的切分次数
  moveNoDown: 0,    // 无 pointerdown 直接收到 move，兜底开始新笔
  coalesced: 0,     // pointermove 携带的合并事件数量（iOS 合并证据）
  last: '-'
})
let tapN = 0
let tapTimer = null
function tapDiag() {
  tapN++
  if (tapTimer) clearTimeout(tapTimer)
  tapTimer = setTimeout(() => { tapN = 0 }, 1200)
  if (tapN >= 3) { tapN = 0; debugOn.value = !debugOn.value }
}
let origin = { left: 0, top: 0 }
let lpTimer = null        // 长按橡皮擦图标的定时器
let lpFired = false       // 长按已触发，忽略随后跟出的 click
let penActive = false     // 手写笔是否正在书写
let lastPenTime = 0       // 手写笔最后活动时间（用于笔离开后的短暂防误触）
let penSeen = false       // 本次草稿是否出现过手写笔（进入"手写笔模式"后手指/手掌不落笔）
// 该设备是否出现过手写笔（持久化记住：只要检测到笔，之后手指/手掌一律不落笔）
const PEN_KEY = 'scratch_pen_detected'
const penAvailable = ref(false)
try { penAvailable.value = !!localStorage.getItem(PEN_KEY) } catch (err) {}

// 记录"本设备有手写笔"：笔尖落笔或悬停（Apple Pencil 悬停也会触发 pointerType==='pen'）
function markPenAvailable() {
  if (!penAvailable.value) {
    penAvailable.value = true
    try { localStorage.setItem(PEN_KEY, '1') } catch (err) {}
  }
  if (props.visible) enterPenMode()
}

// 进入手写笔模式：丢弃此前手指/手掌误触留下的笔画
// （书写时手掌通常先于笔尖接触屏幕，这些"笔画"几乎都是误触）
function enterPenMode() {
  penSeen = true
  if (drawing && current && current.src === 'touch') {
    drawing = false
    current = null
    redraw()
  }
  const now = Date.now()
  const kept = strokes.value.filter((s) => !(s.src === 'touch' && now - (s.t0 || 0) < 2000))
  if (kept.length !== strokes.value.length) {
    strokes.value = kept
    redraw()
  }
  clearOverlay()
}

// 是否应忽略这根手指（设备存在手写笔 → 只有手写笔能书写，手指与手掌一律不落笔）
function shouldIgnoreTouch(e) {
  if (e.pointerType !== 'touch') return false
  if (penAvailable.value || penSeen) return true
  return penActive || Date.now() - lastPenTime < 800
}

// 全局探测手写笔：即使没在草稿里，只要出现过笔尖（落笔或悬停）就记住这台设备有笔
function onGlobalPenEvent(e) {
  if (e.pointerType === 'pen') markPenAvailable()
}

// 草稿打开时：除草稿遮罩与计算器浮窗外的元素一律不接收指针/点击事件。
// CSS 的 pointer-events 在 iPad 上仍可能让底层按钮被选中（手写笔拖画时会把
// 「← 上一题」的文字选中并弹出系统菜单），这里再用捕获阶段彻底拦截兜底。
function globalGuard(e) {
  if (!props.visible) return
  const t = e.target
  if (t && t.closest && (t.closest('.scratch-mask') || t.closest('.calc-float'))) return
  e.stopPropagation()
  if (e.cancelable) e.preventDefault()
}

// ===== 画布尺寸（按设备像素比放大，避免模糊） =====
function setupCanvas() {
  diag.setup++
  const el = canvasEl.value
  if (!el) return
  if (current) commitCurrent()   // 若有一笔正在画，先收进去，避免重设画布时墨迹被清掉
  const r = el.getBoundingClientRect()
  origin.left = r.left
  origin.top = r.top
  const dpr = window.devicePixelRatio || 1
  const w = Math.max(1, Math.round(r.width * dpr))
  const h = Math.max(1, Math.round(r.height * dpr))
  el.width = w
  el.height = h
  ctx = el.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  const ov = overlayEl.value
  if (ov) {
    ov.width = w
    ov.height = h
    octx = ov.getContext('2d')
    octx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }
  redraw()
}

function brushWidth(s) {
  return s.tool === 'eraser' ? s.size * 2.5 : s.size
}

function applyStyle(s, g = ctx) {
  g.globalCompositeOperation = s.tool === 'eraser' ? 'destination-out' : 'source-over'
  g.strokeStyle = s.color
  g.lineWidth = brushWidth(s)
  g.lineCap = 'round'
  g.lineJoin = 'round'
}

function drawStroke(s, g = ctx) {
  applyStyle(s, g)
  // 画笔 / 橡皮：折线
  if (s.tool === 'pen' || s.tool === 'eraser') {
    if (s.points.length === 1) {
      const p = s.points[0]
      g.beginPath()
      g.arc(p.x, p.y, brushWidth(s) / 2, 0, Math.PI * 2)
      g.fillStyle = s.color
      g.fill()
      return
    }
    g.beginPath()
    g.moveTo(s.points[0].x, s.points[0].y)
    for (let i = 1; i < s.points.length; i++) g.lineTo(s.points[i].x, s.points[i].y)
    g.stroke()
    return
  }
  // 预设图形
  if (s.tool === 'line') {
    g.beginPath()
    g.moveTo(s.x1, s.y1)
    g.lineTo(s.x2, s.y2)
    g.stroke()
  } else if (s.tool === 'rect') {
    g.beginPath()
    g.rect(s.x1, s.y1, s.x2 - s.x1, s.y2 - s.y1)
    g.stroke()
  } else if (s.tool === 'circle') {
    const r = Math.hypot(s.x2 - s.x1, s.y2 - s.y1)
    g.beginPath()
    g.arc(s.x1, s.y1, r, 0, Math.PI * 2)
    g.stroke()
  }
}

// 顶层画布：清空图形预览
function clearOverlay() {
  const ov = overlayEl.value
  if (!octx || !ov) return
  octx.save()
  octx.setTransform(1, 0, 0, 1, 0, 0)
  octx.clearRect(0, 0, ov.width, ov.height)
  octx.restore()
  octx.globalCompositeOperation = 'source-over'
}

// 图形实时预览：只重画顶层那一条路径，开销极小（图形跟手）
function previewShape(s) {
  if (!octx) return
  clearOverlay()
  if (s) drawStroke(s, octx)
}

// 整幅重绘（撤销、清空、尺寸变化时用）
function redraw() {
  if (!ctx || !canvasEl.value) return
  ctx.save()
  ctx.setTransform(1, 0, 0, 1, 0, 0)
  ctx.clearRect(0, 0, canvasEl.value.width, canvasEl.value.height)
  ctx.restore()
  ctx.globalCompositeOperation = 'source-over'
  // 注意：不能用 forEach(drawStroke)——forEach 会把下标当第二个参数传进去，
  // 而 drawStroke(s, g) 的 g 是画布上下文，传数字会直接抛错
  for (const s of strokes.value) drawStroke(s)
  ctx.globalCompositeOperation = 'source-over'
}

// ===== 绘制交互 =====
// 拦截草稿内的触摸事件，别让它冒泡到 document 的边缘滑动导航
function stopTouch(e) {
  e.stopPropagation()
}

function pos(e) {
  return { x: e.clientX - origin.left, y: e.clientY - origin.top }
}

function onPointerDown(e) {
  if (e.button !== undefined && e.button !== 0) { diag.downBtn++; return }
  // 防误触：手写笔模式下，手指与手掌一律不落笔（可正常垫手书写）
  if (shouldIgnoreTouch(e)) { diag.downTouch++; return }
  // 快速连笔时，上一笔的 pointerup 可能晚于这一笔的 pointerdown 到达、甚至直接丢失。
  // 新的一笔下笔即视为上一笔已结束：取消延迟收笔并把上一笔正常入库，再开始新的一笔
  if (current) commitCurrent()
  if (e.pointerType === 'pen') {
    // 笔尖出现：记住本设备有手写笔，进入手写笔模式（丢掉先前手指/手掌的误触笔画）
    markPenAvailable()
    penActive = true
    lastPenTime = Date.now()
  }
  e.preventDefault()
  const el = canvasEl.value
  if (!el || !ctx) { diag.downNoEl++; return }
  diag.down++
  // 注意：这里不调用 setPointerCapture —— 在部分 iPadOS Safari 上，指针捕获会
  // 干扰后续笔画的指针事件投递/画布状态，导致已接受的笔迹没能留在画面上
  const p = pos(e)

  // 橡皮擦「按对象擦除」：点中哪一笔就删掉整笔，不进入绘制流程
  if (tool.value === 'eraser' && eraserMode.value === 'object') {
    erasingObject = true
    erasingPid = e.pointerId
    eraseObjectAt(p.x, p.y)
    return
  }

  drawing = true
  lastMoveTs = 0          // 重置，让第一笔不会被"间隙检测"误触发切分
  const base = { tool: tool.value, color: color.value, size: size.value, src: e.pointerType, pid: e.pointerId, dts: e.timeStamp, t0: Date.now() }

  if (base.tool === 'pen' || base.tool === 'eraser') {
    current = { ...base, points: [p] }
    drawStroke(current)          // 单点也留一个圆点
  } else {
    current = { ...base, x1: p.x, y1: p.y, x2: p.x, y2: p.y }
    previewShape(current)
  }
}

function onPointerMove(e) {
  // 防误触：手写笔模式下，手指/手掌移动一律忽略（手掌垫手不会破坏笔画）
  if (shouldIgnoreTouch(e)) { diag.moveTouch++; return }
  // 按对象擦除：按住拖动可连续删掉扫过的笔画
  if (erasingObject) {
    if (e.pointerId !== erasingPid) return
    e.preventDefault()
    const p = pos(e)
    eraseObjectAt(p.x, p.y)
    return
  }
  if (e.pointerType === 'pen') {
    diag.last = `b=${e.buttons} p=${(e.pressure || 0).toFixed(2)} id=${e.pointerId} ts=${Math.round(e.timeStamp)}`
    // iOS Safari 合并 pointerdown/move 时，合并事件可能包含额外的坐标数据
    try {
      const ce = e.getCoalescedEvents ? e.getCoalescedEvents() : null
      if (ce && ce.length > 1) diag.coalesced++
    } catch (err) {}
  }
  const p = pos(e)
  const now = e.timeStamp

  // ===== 隐式笔画切分 & pointerdown 兜底 =====
  // iPadOS Safari 在快速书写时会**合并/跳过 pointerdown**事件，导致我们收不到
  // 完整的 down-up 配对。以下两个机制独立于 pointerdown/pointerup：
  //
  // 1) 间隙切分：正在 drawing 时，如果当前 move 距上一次 move 时间/空间间隙过大，
  //    说明 Safari 合并了"抬笔→落笔"动作——收掉现有笔，当前 move 作为新笔起点
  // 2) pointerdown 兜底：不在 drawing 时收到了 move——说明 pointerdown 被跳过了，
  //    直接用当前 move 的点作为新笔起点开始画
  //
  // 这两个分支必须在所有守卫之前，因为它们正是要"绕开 pointerdown 缺失"的场景
  if (drawing && current && ctx) {
    // 间隙切分判定：时间间隙（> STROKE_GAP_T ms 无 move）或空间间隙（> STROKE_GAP_S px）
    // 满足任一即视为上一笔已结束
    let gap = false
    if (lastMoveTs > 0 && now - lastMoveTs > STROKE_GAP_T) gap = true
    if (!gap && (current.tool === 'pen' || current.tool === 'eraser')) {
      const last = current.points[current.points.length - 1]
      if (Math.hypot(p.x - last.x, p.y - last.y) > STROKE_GAP_S) gap = true
    }
    if (gap) {
      diag.moveSplit++
      commitCurrent()
      // 用当前这个 move 点作为新笔起点（pointerdown 可能被 Safari 跳过了）
      if (e.pointerType === 'pen') {
        markPenAvailable()
        penActive = true
        lastPenTime = Date.now()
      }
      const base = {
        tool: tool.value, color: color.value, size: size.value,
        src: e.pointerType, pid: e.pointerId, dts: e.timeStamp, t0: Date.now()
      }
      if (base.tool === 'pen' || base.tool === 'eraser') {
        current = { ...base, points: [p] }
        drawStroke(current)
      } else {
        current = { ...base, x1: p.x, y1: p.y, x2: p.x, y2: p.y }
        previewShape(current)
      }
      lastMoveTs = now
      return
    }
  } else if (!drawing && ctx) {
    // pointerdown 被 Safari 跳过了，但我们收到了 move——直接开始新笔画
    diag.moveNoDown++
    if (e.pointerType === 'pen') {
      markPenAvailable()
      penActive = true
      lastPenTime = Date.now()
    }
    const base = {
      tool: tool.value, color: color.value, size: size.value,
      src: e.pointerType, pid: e.pointerId, dts: e.timeStamp, t0: Date.now()
    }
    drawing = true
    if (base.tool === 'pen' || base.tool === 'eraser') {
      current = { ...base, points: [p] }
      drawStroke(current)
    } else {
      current = { ...base, x1: p.x, y1: p.y, x2: p.x, y2: p.y }
      previewShape(current)
    }
    lastMoveTs = now
    return
  }

  // ===== 常规绘制路径 =====
  if (!ctx) return
  if (e.pointerId !== current.pid) { diag.movePid++; return }
  e.preventDefault()
  diag.move++
  lastMoveTs = now

  if (current.tool === 'pen' || current.tool === 'eraser') {
    current.points.push(p)
    applyStyle(current)
    ctx.beginPath()
    ctx.moveTo(current.points[current.points.length - 2].x, current.points[current.points.length - 2].y)
    ctx.lineTo(p.x, p.y)
    ctx.stroke()
  } else {
    current.x2 = p.x
    current.y2 = p.y
    previewShape(current)
  }
}

function onPointerUp(e) {
  if (e && e.pointerType === 'pen') { penActive = false; lastPenTime = Date.now() }
  if (erasingObject && (!e || e.pointerId === erasingPid)) erasingObject = false
  if (!drawing || !current) return
  // 迟到的上一笔 up：事件生成时间早于当前这笔的落笔时间，直接忽略（不能把当前笔误收笔）
  if (e && e.timeStamp < current.dts) { diag.upTs++; return }
  // pid 不同也不是当前这笔的 up
  if (e && e.pointerId !== current.pid) { diag.upPid++; return }
  diag.up++
  lastMoveTs = 0           // 重置：一笔结束了，下一笔的 move 不会触发间隙切分误判
  commitCurrent()
}

// 收笔：把正在画的这一笔提交进 strokes（撤销/清空/切题时才会整体重绘）
function commitCurrent() {
  if (!current) return
  diag.commit++
  // 记录每条笔画的 points 数量分布，诊断"笔画断续"：
  // 若 minPts 极低（<3），说明某些笔画只有极少的点，必然看起来断续
  if (current.tool === 'pen' || current.tool === 'eraser') {
    const n = current.points.length
    const total = strokes.value.reduce((a, s) => a + (s.points ? s.points.length : 0), 0)
    diag.avgPts = Math.round((total + n) / (strokes.value.length + 1))
    diag.minPts = diag.minPts === 0 ? n : Math.min(diag.minPts, n)
  }
  const isShape = current.tool === 'line' || current.tool === 'rect' || current.tool === 'circle'
  // 图形拖动距离太小视为误触，直接撤掉预览不留痕迹
  const tooSmall = isShape && Math.hypot(current.x2 - current.x1, current.y2 - current.y1) < 3
  if (tooSmall) {
    clearOverlay()
  } else if (isShape) {
    // 画到正式的底层画布上
    strokes.value = [...strokes.value, current]
    redraw()
    clearOverlay()
  } else {
    strokes.value = [...strokes.value, current]
  }
  current = null
  drawing = false
  if (ctx) ctx.globalCompositeOperation = 'source-over'
}

// ===== 撤销 / 清空 =====
function undo() {
  diag.undo++
  if (current) commitCurrent()   // 若还有一笔正在画（极少见），先收进去再撤销
  if (strokes.value.length === 0) return
  strokes.value = strokes.value.slice(0, -1)
  redraw()
  clearOverlay()
}

function clearAll() {
  diag.clear++
  if (current) commitCurrent()
  if (strokes.value.length === 0) return
  strokes.value = []
  redraw()
  clearOverlay()
}

// ===== 橡皮擦：按对象擦除 =====
// 点到线段的距离
function distToSegment(px, py, x1, y1, x2, y2) {
  const dx = x2 - x1
  const dy = y2 - y1
  const len2 = dx * dx + dy * dy
  let t = len2 === 0 ? 0 : ((px - x1) * dx + (py - y1) * dy) / len2
  t = Math.max(0, Math.min(1, t))
  return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
}

// 判断触点是否命中某一笔（阈值留出手指点选的余量）
function hitStroke(s, x, y) {
  const tol = Math.max(12, brushWidth(s) / 2 + 6)
  if (s.tool === 'pen' || s.tool === 'eraser') {
    const pts = s.points
    if (pts.length === 1) return Math.hypot(x - pts[0].x, y - pts[0].y) <= tol
    for (let i = 1; i < pts.length; i++) {
      if (distToSegment(x, y, pts[i - 1].x, pts[i - 1].y, pts[i].x, pts[i].y) <= tol) return true
    }
    return false
  }
  if (s.tool === 'line') return distToSegment(x, y, s.x1, s.y1, s.x2, s.y2) <= tol
  if (s.tool === 'rect') {
    const x1 = Math.min(s.x1, s.x2)
    const x2 = Math.max(s.x1, s.x2)
    const y1 = Math.min(s.y1, s.y2)
    const y2 = Math.max(s.y1, s.y2)
    return distToSegment(x, y, x1, y1, x2, y1) <= tol ||
      distToSegment(x, y, x2, y1, x2, y2) <= tol ||
      distToSegment(x, y, x2, y2, x1, y2) <= tol ||
      distToSegment(x, y, x1, y2, x1, y1) <= tol
  }
  if (s.tool === 'circle') {
    const r = Math.hypot(s.x2 - s.x1, s.y2 - s.y1)
    return Math.abs(Math.hypot(x - s.x1, y - s.y1) - r) <= tol
  }
  return false
}

// 从后往前找第一笔命中的并整笔删除（后画的在上层，优先删）
function eraseObjectAt(x, y) {
  const list = strokes.value
  for (let i = list.length - 1; i >= 0; i--) {
    if (hitStroke(list[i], x, y)) {
      const next = list.slice()
      next.splice(i, 1)
      strokes.value = next
      redraw()
      return
    }
  }
}

// ===== 长按橡皮擦图标切换模式 =====
function onEraserDown() {
  lpFired = false
  if (lpTimer) clearTimeout(lpTimer)
  lpTimer = setTimeout(() => {
    lpTimer = null
    lpFired = true
    eraserMode.value = eraserMode.value === 'object' ? 'stroke' : 'object'
    tool.value = 'eraser'
  }, 500)
}

function onEraserUp() {
  if (lpTimer) { clearTimeout(lpTimer); lpTimer = null }
}

function pickTool(t) {
  // 长按已经切换过模式，忽略长按之后跟出来的这次 click
  if (t.key === 'eraser' && lpFired) { lpFired = false; return }
  tool.value = t.key
}

// ===== 显示 / 隐藏 =====
// 锁定页面滚动：草稿固定在屏幕上，不能让底下的题目滚动错位
// 同时补偿滚动条宽度，避免打开草稿时页面横向跳动
let prevPaddingRight = ''
function lockScroll(lock) {
  // 草稿打开期间给 body 挂 scratch-open 类：全局 CSS 会关闭底层页面的 pointer-events，
  // 防止 iPad 手写笔/手掌穿透触发「上一题」等按钮导致断笔
  document.body.classList.toggle('scratch-open', lock)
  if (lock) {
    const sw = window.innerWidth - document.documentElement.clientWidth
    prevPaddingRight = document.body.style.paddingRight
    document.body.style.overflow = 'hidden'
    if (sw > 0) document.body.style.paddingRight = sw + 'px'
    // 关掉根元素的横向 overscroll，避免浏览器把边缘划动当成「返回上一页」
    document.documentElement.style.overscrollBehaviorX = 'none'
    document.body.style.overscrollBehaviorX = 'none'
  } else {
    document.body.style.overflow = ''
    document.body.style.paddingRight = prevPaddingRight
    document.documentElement.style.overscrollBehaviorX = ''
    document.body.style.overscrollBehaviorX = ''
  }
}

// 说明：iOS Safari 的「左缘右滑=返回」是系统手势，JS 无法阻止。
// 曾试过 history 哨兵抵消，但系统手势的翻页动画照旧、翻出来的是同一张页面，观感更差，
// 因此这里不做处理——让它按系统行为正常返回上一级。
watch(() => props.visible, async (v) => {
  lockScroll(v)
  if (!v) {
    // 关掉草稿前若还有一笔正在画，先收进去（墨迹已画在画布上）
    if (current) commitCurrent()
    drawing = false
    erasingObject = false
    current = null
    clearOverlay()
    return
  }
  // 每次重新打开草稿：重置"本次会话"的手写笔状态；
  // 若本设备已检测到过手写笔（penAvailable），手指从一开始就不落笔
  penActive = false
  penSeen = false
  lastPenTime = 0
  await nextTick()
  setupCanvas()
})

// 切题自动清空
watch(() => props.questionKey, () => {
  diag.qkChange++
  strokes.value = []
  current = null
  drawing = false
  erasingObject = false
  // 重置手写笔状态：新题默认允许手指书写，出现手写笔后再进入防误触模式
  penActive = false
  penSeen = false
  lastPenTime = 0
  if (props.visible) nextTick(() => { setupCanvas(); clearOverlay() })
})

// 记录 strokes 数组最近一次变化（旧长度→新长度）：若出现 n < o 的"减少"，
// 说明有代码路径在 commit 之后删掉了笔画（undo/clearAll/切题/enterPenMode 等）
watch(strokes, (n, o) => {
  diag.strokesWatch = `${o ? o.length : 0}>${n ? n.length : 0}`
})

function onResize() {
  if (props.visible) setupCanvas()
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  // 全局探测手写笔（落笔 / 悬停都算），并在一开始就拦掉草稿外的指针与选中事件
  window.addEventListener('pointerdown', onGlobalPenEvent, true)
  window.addEventListener('pointerover', onGlobalPenEvent, true)
  for (const type of ['pointerdown', 'click', 'dblclick', 'selectstart', 'contextmenu']) {
    document.addEventListener(type, globalGuard, true)
  }
  document.addEventListener('touchstart', globalGuard, { capture: true, passive: false })
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  window.removeEventListener('pointerdown', onGlobalPenEvent, true)
  window.removeEventListener('pointerover', onGlobalPenEvent, true)
  for (const type of ['pointerdown', 'click', 'dblclick', 'selectstart', 'contextmenu']) {
    document.removeEventListener(type, globalGuard, true)
  }
  document.removeEventListener('touchstart', globalGuard, { capture: true, passive: false })
  if (lpTimer) { clearTimeout(lpTimer); lpTimer = null }
  lockScroll(false)
})
</script>

<style scoped>
.scratch-mask {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: transparent;
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
  touch-action: none;
  /* 抑制浏览器的边缘返回/下拉刷新（与边缘滑动导航冲突） */
  overscroll-behavior: none;
}

.scratch-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  touch-action: none;
  cursor: crosshair;
}

/* 顶层预览层：只负责显示正在拖动的图形，不接收指针事件 */
.scratch-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.scratch-hint {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 13px;
  padding: 6px 14px;
  border-radius: 14px;
  pointer-events: none;
  white-space: nowrap;
}

/* 真机诊断浮层：定位完成后可整块删除（含上方模板与脚本里的 diag/debugOn/tapDiag） */
.scratch-diag {
  position: absolute;
  top: 74px;
  left: 10px;
  max-width: 92vw;
  padding: 6px 8px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.78);
  color: #7dffb0;
  font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 11px;
  line-height: 1.5;
  white-space: nowrap;
  overflow: hidden;
  pointer-events: none;
}

/* 只有点这个按钮才能退出 */
.scratch-close {
  position: absolute;
  top: 16px;
  right: 20px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  font-size: 26px;
  line-height: 1;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
}

.scratch-close:hover {
  background: rgba(0, 0, 0, 0.68);
}

/* 底部工具栏 */
.scratch-bar {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 8px 10px calc(8px + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.94);
  border-top: 1px solid #e6e6e6;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
  /* 长按橡皮擦图标时不要弹出系统菜单 */
  -webkit-touch-callout: none;
  user-select: none;
}

.bar-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.bar-label {
  font-size: 12px;
  color: #888;
  margin: 0 2px;
}

.bar-sep {
  width: 1px;
  height: 22px;
  background: #e0e0e0;
  margin: 0 4px;
}

/* 橡皮擦线条图标 */
.tool-svg {
  width: 19px;
  height: 19px;
  display: block;
}

/* 橡皮擦模式提示 */
.eraser-tip {
  font-size: 12px;
  color: #666;
  background: #f2f7ff;
  border: 1px solid #d8e6f8;
  border-radius: 8px;
  padding: 3px 10px;
  max-width: 96vw;
  text-align: center;
}

.tool-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  height: 38px;
  padding: 0 8px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  font-size: 17px;
  line-height: 1;
  color: #555;
  cursor: pointer;
  transition: all 0.15s;
  touch-action: manipulation;
}

.tool-btn:hover:not(:disabled) {
  border-color: #4a90d9;
  color: #4a90d9;
}

.tool-btn.active {
  border-color: #4a90d9;
  background: #e8f2ff;
  color: #4a90d9;
}

.tool-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.size-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
}

.size-btn.active {
  border-color: #4a90d9;
  background: #e8f2ff;
}

.size-dot {
  display: block;
  border-radius: 50%;
  background: #555;
}

.size-btn.active .size-dot {
  background: #4a90d9;
}

.color-btn {
  width: 26px;
  height: 26px;
  border: 2px solid #fff;
  border-radius: 50%;
  box-shadow: 0 0 0 1px #d9d9d9;
  cursor: pointer;
}

.color-btn.active {
  box-shadow: 0 0 0 2px #4a90d9;
}

@media (max-width: 600px) {
  .tool-btn {
    min-width: 36px;
    padding: 0 6px;
  }
  .bar-label {
    display: none;
  }
}
</style>