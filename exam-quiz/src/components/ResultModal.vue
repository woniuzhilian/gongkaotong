<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content" ref="modalContentEl" :style="dragStyle">
      <div class="modal-header" @pointerdown="startDrag">
        <span class="result-tag" :class="isCorrect ? 'correct' : 'wrong'">
          {{ isCorrect ? '回答正确' : '回答错误' }}
        </span>
        <button
          v-if="showRemoveWrong"
          class="remove-wrong-btn"
          :disabled="removed"
          @click="onRemoveWrong"
        >
          {{ removed ? '已移出' : '移出错题本' }}
        </button>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>

      <div class="modal-body">
        <div class="answer-row">
          <span class="label">你的答案：</span>
          <span class="user-answer" :class="isCorrect ? 'correct' : 'wrong'">
            {{ userAnswer || '未作答' }}
          </span>
        </div>
        <div class="answer-row">
          <span class="label">正确答案：</span>
          <span class="correct-answer">{{ question.answer }}</span>
        </div>

        <div class="analysis-section">
          <div class="analysis-title">答案解析</div>
          <!-- 正常显示解析 -->
          <div class="analysis-content" v-if="!isGuest" v-html="renderedAnalysis"></div>
          <!-- 游客模式：解析替换为登录提示 -->
          <div class="guest-analysis-tip" v-else>
            <p>游客模式无法查看解析，如需查看答案解析请 <span class="login-link" @click="goLogin">登录</span>。</p>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <div class="footer-btns">
          <button
            class="knowledge-btn"
            :class="{ disabled: !canOpenKnowledge }"
            :disabled="!canOpenKnowledge"
            :title="knowledgeBtnTitle"
            @click="openKnowledge"
          >
            知识点扩展
          </button>
          <button class="confirm-btn" @click="$emit('next')">
            {{ isLast ? '查看结果' : '下一题' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 知识点扩展弹窗 -->
    <div v-if="showKnowledge" class="knowledge-overlay" @click.self="showKnowledge = false">
      <div class="knowledge-content">
        <div class="knowledge-header">
          <h3>知识点扩展 · {{ question.smallSubject }}</h3>
          <button class="close-btn" @click="showKnowledge = false">&times;</button>
        </div>
        <div class="knowledge-body" v-html="renderedKnowledge"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import katex from 'katex'
import knowledgeExt from '../data/knowledgeExt.json'

const router = useRouter()

const props = defineProps({
  visible: { type: Boolean, default: false },
  question: { type: Object, required: true },
  userAnswer: { type: String, default: '' },
  isLast: { type: Boolean, default: false },
  isGuest: { type: Boolean, default: false },
  bigSubject: { type: String, default: '' },
  isInWrong: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'next', 'remove-wrong'])

// ===== 桌面（鼠标环境）拖动解析窗：在 header 上按住拖动整个窗口 =====
// 手机/平板（触屏）不进入拖动逻辑，保持原居中动画
const modalContentEl = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
let dragState = null

const dragStyle = computed(() => ({
  transform: `translate(${dragOffset.value.x}px, ${dragOffset.value.y}px)`
}))

function startDrag(e) {
  // 仅鼠标按下才允许拖动；触屏环境（pointerType=touch/pen）保持现状不可拖动
  if (e.pointerType && e.pointerType !== 'mouse') return
  if (e.button !== 0) return
  if (e.target.closest('.close-btn')) return
  const el = modalContentEl.value
  if (!el) return
  e.preventDefault()
  const rect = el.getBoundingClientRect()
  dragState = {
    id: e.pointerId,
    sx: e.clientX, sy: e.clientY,
    baseLeft: rect.left, baseTop: rect.top
  }
  window.addEventListener('pointermove', onDragMove)
  window.addEventListener('pointerup', endDrag)
  window.addEventListener('pointercancel', endDrag)
}

function onDragMove(e) {
  if (!dragState || e.pointerId !== dragState.id) return
  const el = modalContentEl.value
  if (!el) return
  // 限制在视口内：至少露出标题栏与部分内容，避免拖丢
  const visLeft = Math.min(Math.max(dragState.baseLeft + e.clientX - dragState.sx, 0), window.innerWidth - 80)
  const visTop = Math.min(Math.max(dragState.baseTop + e.clientY - dragState.sy, 0), window.innerHeight - 60)
  dragOffset.value = { x: visLeft - dragState.baseLeft, y: visTop - dragState.baseTop }
}

function endDrag(e) {
  if (dragState && (!e || e.pointerId === dragState.id)) dragState = null
  window.removeEventListener('pointermove', onDragMove)
  window.removeEventListener('pointerup', endDrag)
  window.removeEventListener('pointercancel', endDrag)
}

// 弹窗重新打开时复位位置
watch(() => props.visible, (v) => {
  if (v) dragOffset.value = { x: 0, y: 0 }
})

const showKnowledge = ref(false)
// 本题是否已在本弹窗内执行过「移出错题本」
const removed = ref(false)
// 仅当本题在错题本中时显示按钮；移除后短暂保留「已移出」禁用态作反馈
const showRemoveWrong = computed(() => props.isInWrong || removed.value)

// 切题时自动关闭知识点弹窗，并重置移除状态
watch(() => props.question, () => {
  showKnowledge.value = false
  removed.value = false
})

function onRemoveWrong() {
  if (removed.value) return
  removed.value = true
  emit('remove-wrong')
}

const isCorrect = computed(() => props.userAnswer === props.question.answer)

// 知识点扩展：为该题单独编写过内容时就可用
const knowledgeHtml = computed(() => {
  const q = props.question
  if (!q) return ''
  return knowledgeExt['q:' + q.id] || ''
})
const hasKnowledge = computed(() => !!knowledgeHtml.value)

// 能否打开知识点扩展：游客或无内容时不可
const canOpenKnowledge = computed(() => !props.isGuest && hasKnowledge.value)

const knowledgeBtnTitle = computed(() => {
  if (props.isGuest) return '游客模式无法查看知识点扩展，请先登录'
  if (!hasKnowledge.value) return '该题暂无知识点扩展'
  return '查看本题考查的知识点扩展'
})

const renderedKnowledge = computed(() => renderLatex(knowledgeHtml.value))

function openKnowledge() {
  if (props.isGuest) {
    alert('游客模式无法查看知识点扩展，请先登录')
    return
  }
  showKnowledge.value = true
}

function goLogin() {
  // 记录当前做题页作为来源，登录成功/游客继续时跳回来
  // 同时带 from=result query 参数让 AuthView 显示顶部「← 返回」按钮
  sessionStorage.setItem('auth_return_to', router.currentRoute.value.fullPath)
  emit('close')
  router.push({ path: '/auth', query: { from: 'result' } })
}

function renderLatex(text) {
  if (!text) return ''
  return text.replace(/\$([^$]+)\$/g, (match, formula) => {
    try {
      return katex.renderToString('\\displaystyle ' + formula, {
        throwOnError: false,
        displayMode: false
      })
    } catch (e) {
      return match
    }
  })
}

const renderedAnalysis = computed(() => {
  return renderLatex(props.question.analysis || '')
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 560px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  user-select: none;
  -webkit-user-select: none;
}

/* 仅桌面鼠标环境：header 提示可拖动 */
@media (hover: hover) and (pointer: fine) {
  .modal-header {
    cursor: move;
  }
}

.result-tag {
  font-size: 18px;
  font-weight: bold;
  padding: 4px 16px;
  border-radius: 20px;
}

.result-tag.correct {
  background: #f6ffed;
  color: #52c41a;
}

.result-tag.wrong {
  background: #fff2f0;
  color: #ff4d4f;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

/* 头部中部「移出错题本」按钮：错题本主题的描边胶囊；
   字号/字重与左侧「回答正确/错误」标签统一（18px bold） */
.remove-wrong-btn {
  background: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
  border-radius: 20px;
  font-size: 18px;
  font-weight: bold;
  padding: 4px 12px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.remove-wrong-btn:hover:not(:disabled) {
  background: #ff4d4f;
  color: #fff;
}

.remove-wrong-btn:disabled {
  background: #f5f5f5;
  color: #bbb;
  border-color: #e0e0e0;
  cursor: default;
}

.modal-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.answer-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 15px;
}

.label {
  color: #666;
  min-width: 80px;
}

.user-answer.correct, .correct-answer {
  color: #52c41a;
  font-weight: bold;
  font-size: 18px;
}

.user-answer.wrong {
  color: #ff4d4f;
  font-weight: bold;
  font-size: 18px;
}

.analysis-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.analysis-title {
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
  font-size: 15px;
}

.analysis-content {
  font-size: 15px;
  line-height: 1.8;
  color: #555;
  word-break: break-word;
}

.analysis-content :deep(img) {
  max-width: 100%;
  height: auto;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
  text-align: center;
}

.footer-btns {
  display: flex;
  gap: 12px;
}

.footer-btns .knowledge-btn,
.footer-btns .confirm-btn {
  flex: 1;
  padding: 10px 4px;
}

.knowledge-btn {
  background: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.knowledge-btn:hover:not(.disabled) {
  background: #fa8c16;
  color: #fff;
}

.knowledge-btn.disabled {
  background: #f5f5f5;
  color: #bbb;
  border-color: #e0e0e0;
  cursor: not-allowed;
}

/* 游客模式登录提示 */
.guest-analysis-tip {
  font-size: 14px;
  line-height: 1.8;
  color: #888;
  padding: 12px;
  background: #f5f7ff;
  border-radius: 8px;
  text-align: center;
}
.guest-analysis-tip p {
  margin: 0;
}
.guest-analysis-tip .login-link {
  color: #4a90d9;
  cursor: pointer;
  text-decoration: underline;
}

/* 知识点扩展弹窗 */
.knowledge-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  padding: 16px;
}

.knowledge-content {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 640px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.knowledge-header h3 {
  margin: 0;
  font-size: 17px;
  color: #fa8c16;
}

.knowledge-body {
  padding: 18px 20px;
  overflow-y: auto;
  font-size: 15px;
  line-height: 1.8;
  color: #444;
  word-break: break-word;
}

.knowledge-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0;
  font-size: 15px;
}

.knowledge-body :deep(td), .knowledge-body :deep(th) {
  border: 1px solid #e0e0e0;
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
}

.knowledge-body :deep(th) {
  background: #fff7e6;
  color: #d46b08;
}

.knowledge-body :deep(h4) {
  margin: 14px 0 6px;
  color: #333;
  font-size: 15px;
}

.knowledge-body :deep(ul) {
  margin: 6px 0;
  padding-left: 20px;
}

.knowledge-body :deep(li) {
  margin: 4px 0;
}

.confirm-btn {
  padding: 10px 40px;
  background: #4a90d9;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

.confirm-btn:hover {
  background: #357abd;
}

@media (max-width: 600px) {
  .modal-content {
    max-height: 85vh;
  }
  .modal-body {
    padding: 16px;
  }
}
</style>
