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
    <div class="scratch-hint">在题目上直接书写圈画 · 点右上角 × 退出</div>

    <button class="scratch-close" title="退出草稿" @click="$emit('close')">×</button>

    <!-- 底部 wrapper：scratch-bar 和 scratch-toggle 一起在这里面，toggle 的 100% = wrapper 高度 = bar 高度 -->
    <div class="scratch-bottom-wrap" :class="{ collapsed: barCollapsed }">
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
        <button class="tool-btn calc-launch" title="计算器" @click="$emit('open-calculator')">🧮</button>
      </div>
      <div class="bar-row">
        <span class="bar-label">粗细</span>
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

    <!-- 工具栏收起/展开箭头（绝对定位在 wrapper 内 = scratch-bar 正上方） -->
    <button class="scratch-toggle" @click="barCollapsed = !barCollapsed" :title="barCollapsed ? '展开工具栏' : '收起工具栏'">
      <span class="toggle-arrow">{{ barCollapsed ? '▲' : '▼' }}</span>
    </button>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  // 题目标识：变化时自动清空草稿（切题自动清空）
  questionKey: { type: [String, Number], default: '' }
})

defineEmits(['close', 'open-calculator'])

const canvasEl = ref(null)
const overlayEl = ref(null)
const tool = ref('pen')
const barCollapsed = ref(false)   // 工具栏是否收起
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
let origin = { left: 0, top: 0 }
let lpTimer = null        // 长按橡皮擦图标的定时器
let lpFired = false       // 长按已触发，忽略随后跟出的 click
let penActive = false     // 手写笔是否正在书写
let lastPenTime = 0       // 手写笔最后活动时间（用于笔离开后的短暂防误触）

// ===== 画布尺寸（按设备像素比放大，避免模糊） =====
function setupCanvas() {
  const el = canvasEl.value
  if (!el) return
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
  if (e.button !== undefined && e.button !== 0) return
  // 防误触：手写笔正在使用（或刚用完的短暂间隔内），忽略手指与手掌的触摸
  // 若 localStorage 里有 scratch_pen_detected 标记（设备曾检测到 Apple Pencil），则手指永久忽略
  const penOnly = penActive || Date.now() - lastPenTime < 800 || localStorage.getItem('scratch_pen_detected')
  if (e.pointerType === 'touch' && penOnly) return
  if (e.pointerType === 'pen') {
    penActive = true; lastPenTime = Date.now()
    // 第一次检测到手写笔，写入 localStorage，以后该设备手指一律不落笔
    if (!localStorage.getItem('scratch_pen_detected')) {
      try { localStorage.setItem('scratch_pen_detected', '1') } catch (err) {}
    }
  }
  e.preventDefault()
  const el = canvasEl.value
  if (!el || !ctx) return
  try { el.setPointerCapture(e.pointerId) } catch (err) {}
  const p = pos(e)

  // 橡皮擦「按对象擦除」：点中哪一笔就删掉整笔，不进入绘制流程
  if (tool.value === 'eraser' && eraserMode.value === 'object') {
    erasingObject = true
    eraseObjectAt(p.x, p.y)
    return
  }

  drawing = true
  const base = { tool: tool.value, color: color.value, size: size.value }

  if (base.tool === 'pen' || base.tool === 'eraser') {
    current = { ...base, points: [p] }
    drawStroke(current)          // 单点也留一个圆点
  } else {
    current = { ...base, x1: p.x, y1: p.y, x2: p.x, y2: p.y }
    previewShape(current)
  }
}

function onPointerMove(e) {
  // 防误触：手写笔使用期间，手指/手掌移动一律忽略（避免手掌把笔画擦掉）
  const penOnlyMove = penActive || Date.now() - lastPenTime < 800 || localStorage.getItem('scratch_pen_detected')
  if (e.pointerType === 'touch' && penOnlyMove) return
  // 按对象擦除：按住拖动可连续删掉扫过的笔画
  if (erasingObject) {
    e.preventDefault()
    const p = pos(e)
    eraseObjectAt(p.x, p.y)
    return
  }
  if (!drawing || !current || !ctx) return
  e.preventDefault()
  const p = pos(e)

  if (current.tool === 'pen' || current.tool === 'eraser') {
    const last = current.points[current.points.length - 1]
    if (Math.hypot(p.x - last.x, p.y - last.y) < 1) return
    current.points.push(p)
    // 只画新增的一段，避免每帧整幅重绘
    applyStyle(current)
    ctx.beginPath()
    ctx.moveTo(last.x, last.y)
    ctx.lineTo(p.x, p.y)
    ctx.stroke()
  } else {
    // 图形预览：只重画顶层预览层，边框实时跟手
    current.x2 = p.x
    current.y2 = p.y
    previewShape(current)
  }
}

function onPointerUp(e) {
  if (e && e.pointerType === 'pen') { penActive = false; lastPenTime = Date.now() }
  if (erasingObject) erasingObject = false
  if (!drawing || !current) return
  drawing = false
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
  ctx.globalCompositeOperation = 'source-over'
}

// ===== 撤销 / 清空 =====
function undo() {
  if (strokes.value.length === 0) return
  strokes.value = strokes.value.slice(0, -1)
  redraw()
  clearOverlay()
}

function clearAll() {
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
// ===== iPad 断笔修复：草稿打开时捕获阶段拦截底层事件 =====
// iPad 上用 Apple Pencil 拖画时，笔尖附近的 pointerdown/click 会选中底层文字
// 并弹出系统「拷贝/查询/翻译」菜单，导致笔画被断开。用捕获阶段 global 拦截兜底。
function onGlobalCapture(e) {
  // 草稿画布(.scratch-canvas)、覆盖层(.scratch-overlay)、工具栏(.scratch-bar)、关闭按钮(.scratch-close)、
  // 收起箭头(.scratch-toggle)、提示语(.scratch-hint)、以及计算器(.calc-float) → 放行
  const t = e.target
  if (t && t.closest && (
    t.closest('.scratch-canvas') ||
    t.closest('.scratch-overlay') ||
    t.closest('.scratch-bar') ||
    t.closest('.scratch-close') ||
    t.closest('.scratch-toggle') ||
    t.closest('.scratch-hint') ||
    t.closest('.calc-float')
  )) return  // 草稿层内部的元素，正常派发

  // 底层元素的 pointerdown/click/dblclick/selectstart/contextmenu/touchstart 一律阻止
  if (['pointerdown','click','dblclick','selectstart','contextmenu','touchstart'].includes(e.type)) {
    e.preventDefault()
    e.stopPropagation()
  }
}

function lockScroll(lock) {
  if (lock) {
    const sw = window.innerWidth - document.documentElement.clientWidth
    prevPaddingRight = document.body.style.paddingRight
    document.body.style.overflow = 'hidden'
    if (sw > 0) document.body.style.paddingRight = sw + 'px'
    // 关掉根元素的横向 overscroll，避免浏览器把边缘划动当成「返回上一页」
    document.documentElement.style.overscrollBehaviorX = 'none'
    document.body.style.overscrollBehaviorX = 'none'
    // iPad 断笔修复：body 挂 scratch-open 类 + 捕获阶段全局拦截
    document.body.classList.add('scratch-open')
    document.addEventListener('pointerdown', onGlobalCapture, true)
    document.addEventListener('click', onGlobalCapture, true)
    document.addEventListener('dblclick', onGlobalCapture, true)
    document.addEventListener('selectstart', onGlobalCapture, true)
    document.addEventListener('contextmenu', onGlobalCapture, true)
    document.addEventListener('touchstart', onGlobalCapture, true)
  } else {
    document.body.style.overflow = ''
    document.body.style.paddingRight = prevPaddingRight
    document.documentElement.style.overscrollBehaviorX = ''
    document.body.style.overscrollBehaviorX = ''
    // 移除 iPad 断笔修复
    document.body.classList.remove('scratch-open')
    document.removeEventListener('pointerdown', onGlobalCapture, true)
    document.removeEventListener('click', onGlobalCapture, true)
    document.removeEventListener('dblclick', onGlobalCapture, true)
    document.removeEventListener('selectstart', onGlobalCapture, true)
    document.removeEventListener('contextmenu', onGlobalCapture, true)
    document.removeEventListener('touchstart', onGlobalCapture, true)
  }
}

// 说明：iOS Safari 的「左缘右滑=返回」是系统手势，JS 无法阻止。
// 曾试过 history 哨兵抵消，但系统手势的翻页动画照旧、翻出来的是同一张页面，观感更差，
// 因此这里不做处理——让它按系统行为正常返回上一级。
watch(() => props.visible, async (v) => {
  lockScroll(v)
  if (!v) {
    drawing = false
    erasingObject = false
    current = null
    clearOverlay()
    return
  }
  await nextTick()
  setupCanvas()
})

// 切题自动清空
watch(() => props.questionKey, () => {
  strokes.value = []
  current = null
  drawing = false
  erasingObject = false
  if (props.visible) nextTick(() => { setupCanvas(); clearOverlay() })
})

function onResize() {
  if (props.visible) setupCanvas()
}

onMounted(() => {
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
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

/* 底部 wrapper：绝对定位在 scratch-mask 底部，scratch-bar 在内部正常流 */
.scratch-bottom-wrap {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  transition: transform 0.22s ease, opacity 0.18s ease;
  pointer-events: none;  /* wrapper 自己不拦截 */
}
.scratch-bottom-wrap > * { pointer-events: auto; }
/* 整个 wrapper（bar + toggle）一起滑出屏幕 */
.scratch-bottom-wrap.collapsed {
  transform: translateY(100%);
}
/* 箭头不跟随透明，保持清晰可见 */
.scratch-bottom-wrap.collapsed .scratch-toggle {
  opacity: 1;
}

/* 底部工具栏（在 wrapper 内部，正常流，absolute 由 wrapper 承担） */
.scratch-bar {
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
/* 收起/展开箭头按钮：绝对定位在 wrapper 内 → 100% = wrapper 高度 = scratch-bar 高度 */
.scratch-toggle {
  position: absolute;
  bottom: calc(100% + 4px);
  left: 50%;
  transform: translateX(-50%);
  width: 52px;
  height: 26px;
  padding: 0;
  background: #e8eef5;
  border: 1px solid #c0d0e0;
  border-radius: 13px;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, transform 0.15s;
}
.scratch-toggle:hover { background: #d6e2f0; }
.scratch-toggle:active { background: #c3d3e6; transform: translateX(-50%) scale(0.95); }
.toggle-arrow {
  font-size: 13px;
  color: #4a6fa0;
  font-weight: bold;
  line-height: 1;
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
