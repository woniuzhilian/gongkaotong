<template>
  <div class="question-card">
    <div class="question-header">
      <span class="q-num">{{ question.year }}-{{ question.yearQnum || question.id }}</span>
      <span class="q-progress">{{ currentIndex + 1 }} / {{ total }}</span>
      <button class="report-btn" @click="showReportModal = true" title="报错">⚠️ 报错</button>
    </div>

    <div class="question-content" v-html="renderedQuestion"></div>

    <div class="options">
      <button
        v-for="opt in ['A', 'B', 'C', 'D']"
        :key="opt"
        class="option-btn"
        :class="{
          selected: selectedAnswer === opt,
          correct: locked && question.answer === opt,
          wrong: locked && selectedAnswer === opt && question.answer !== opt,
          disabled: locked
        }"
        :disabled="locked"
        @click="selectOption(opt)"
      >
        <span class="opt-label">{{ opt }}</span>
        <span class="opt-content" v-html="renderOption(opt)"></span>
      </button>
    </div>

    <div class="submit-area" :class="{ multi: locked }">
      <button
        class="dont-know-btn"
        :class="{ active: dontKnow, disabled: locked }"
        :disabled="locked"
        @click="toggleDontKnow"
      >
        我不会
      </button>
      <button
        class="submit-btn"
        :disabled="(!selectedAnswer && !dontKnow) || locked"
        @click="$emit('submit', dontKnow)"
      >
        提交
      </button>
      <div class="result-btns" v-if="locked">
        <button
          class="analysis-btn"
          @click="$emit('analysis')"
        >
          解析
        </button>
        <button
          class="next-btn"
          @click="$emit('next')"
        >
          {{ isLast ? '查看结果' : '下一题' }}
        </button>
      </div>
    </div>
    <!-- 报错反馈弹窗 -->
    <div class="report-mask" v-if="showReportModal" @click.self="showReportModal = false">
      <div class="report-modal">
        <div class="report-header">
          <h3>题目报错</h3>
          <button class="report-close" @click="showReportModal = false">×</button>
        </div>
        <div class="report-body">
          <p class="report-tip">请问哪里有问题？（可多选）</p>
          <div class="report-options">
            <label class="report-option" v-for="part in ['题干', '配图', '选项', '解析']" :key="part">
              <input type="checkbox" :value="part" v-model="selectedParts" />
              <span>{{ part }}</span>
            </label>
          </div>
          <div class="report-textarea">
            <label>详细描述（选填）</label>
            <textarea v-model="reportText" placeholder="请描述具体问题，方便我们修正"></textarea>
          </div>
        </div>
        <div class="report-footer">
          <div class="report-error" v-if="reportError">{{ reportError }}</div>
          <button class="report-cancel" @click="showReportModal = false">取消</button>
          <button class="report-submit" :disabled="reportLoading" @click="submitReport">
            {{ reportLoading ? '提交中...' : '提交反馈' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { submitFeedback } from '../utils/supabase'
import katex from 'katex'

const props = defineProps({
  question: { type: Object, required: true },
  currentIndex: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  locked: { type: Boolean, default: false },
  initialAnswer: { type: String, default: '' }
})

const emit = defineEmits(['submit', 'next', 'select', 'analysis'])

const selectedAnswer = ref(props.initialAnswer || '')
const dontKnow = ref(false)

watch(() => props.question, () => {
  selectedAnswer.value = props.initialAnswer || ''
  dontKnow.value = false
})

watch(() => props.initialAnswer, (val) => {
  selectedAnswer.value = val || ''
})

const isLast = computed(() => props.currentIndex === props.total - 1)

// 报错反馈相关
const showReportModal = ref(false)
const selectedParts = ref([])
const reportText = ref('')
const reportLoading = ref(false)
const reportError = ref('')
const reportSuccess = ref(false)

async function submitReport() {
  reportError.value = ''
  if (selectedParts.value.length === 0) {
    reportError.value = '请至少选择一个出错部位'
    return
  }
  reportLoading.value = true
  try {
    const q = props.question || {}
    const questionId = q.year + "-" + (q.yearQnum || q.id)
    await submitFeedback(
      questionId,
      selectedParts.value,
      reportText.value
    )
    alert('反馈提交成功，感谢您的帮助！')
    showReportModal.value = false
    selectedParts.value = []
    reportText.value = ''
  } catch (err) {
    reportError.value = err.message || '提交失败，请重试'
  } finally {
    reportLoading.value = false
  }
}

// 渲染LaTeX公式
function renderLatex(text) {
  if (!text) return ''
  // 处理 $...$ 公式
  return text.replace(/\$([^$]+)\$/g, (match, formula) => {
    try {
      return katex.renderToString(formula, {
        throwOnError: false,
        displayMode: false
      })
    } catch (e) {
      return match
    }
  })
}

const renderedQuestion = computed(() => {
  return renderLatex(props.question.question || '')
})

function renderOption(opt) {
  return renderLatex(props.question[opt] || '')
}

function selectOption(opt) {
  if (props.locked) return
  selectedAnswer.value = opt
  dontKnow.value = false
  emit('select', opt)
}

function toggleDontKnow() {
  if (props.locked) return
  dontKnow.value = !dontKnow.value
  if (dontKnow.value) {
    selectedAnswer.value = ''
    emit('select', '')
  }
}
</script>

<style scoped>
.question-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.q-num {
  background: #4a90d9;
  color: #fff;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 13px;
}

.q-progress {
  color: #888;
  font-size: 13px;
  padding: 2px 8px;
}

.q-subject, .q-year {
  color: #666;
  font-size: 13px;
  padding: 2px 8px;
  background: #f0f0f0;
  border-radius: 12px;
}

.question-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  margin-bottom: 20px;
  word-break: break-word;
}

.question-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 8px 0;
}

.question-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

.question-content :deep(td), .question-content :deep(th) {
  border: 1px solid #ddd;
  padding: 6px 10px;
  text-align: center;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.option-btn {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  font-size: 15px;
  line-height: 1.6;
}

.option-btn:hover:not(:disabled) {
  border-color: #4a90d9;
  background: #f0f7ff;
}

.option-btn.selected {
  border-color: #4a90d9;
  background: #e8f2ff;
}

.option-btn.correct {
  border-color: #52c41a;
  background: #f6ffed;
}

.option-btn.wrong {
  border-color: #ff4d4f;
  background: #fff2f0;
}

.option-btn:disabled {
  cursor: not-allowed;
}

.opt-label {
  font-weight: bold;
  color: #4a90d9;
  min-width: 24px;
}

.option-btn.correct .opt-label {
  color: #52c41a;
}

.option-btn.wrong .opt-label {
  color: #ff4d4f;
}

.opt-content {
  flex: 1;
  word-break: break-word;
}

.opt-content :deep(img) {
  max-width: 100%;
  height: auto;
}

.submit-area {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
}

.submit-btn, .next-btn, .analysis-btn {
  padding: 12px 36px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

/* 提交后四个按钮：等大、均分一行 */
.submit-area.multi {
  display: flex;
  align-items: stretch;
  gap: 12px;
}

.submit-area.multi .dont-know-btn,
.submit-area.multi .submit-btn,
.submit-area.multi .analysis-btn,
.submit-area.multi .next-btn {
  flex: 1;
  width: auto;
  grid-column: auto;
  justify-self: auto;
  padding: 12px 4px;
}

.submit-area.multi .result-btns {
  display: contents;
}

.submit-btn {
  grid-column: 2;
  justify-self: center;
  background: #4a90d9;
  color: #fff;
  width: 140px;
}

.dont-know-btn {
  grid-column: 1;
  justify-self: start;
  padding: 12px 8px;
  border: 1px solid #4a90d9;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  background: #fff;
  color: #4a90d9;
  transition: all 0.2s;
  width: 140px;
}

.dont-know-btn:hover:not(.disabled) {
  background: #f0f7ff;
}

.dont-know-btn.active {
  background: #4a90d9;
  color: #fff;
}

.dont-know-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.result-btns {
  grid-column: 3;
  justify-self: end;
  display: flex;
  gap: 12px;
}

.submit-btn:hover:not(:disabled) {
  background: #357abd;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.next-btn {
  background: #52c41a;
  color: #fff;
}

.next-btn:hover {
  background: #389e0d;
}

.analysis-btn {
  background: #fff;
  color: #4a90d9;
  border: 1px solid #4a90d9;
}

.analysis-btn:hover {
  background: #4a90d9;
  color: #fff;
}

@media (max-width: 600px) {
  .question-card {
    padding: 14px;
  }
  .question-content {
    font-size: 15px;
  }
  .option-btn {
    padding: 12px;
    font-size: 14px;
  }
  /* 手机竖屏：「我不会」宽度为「提交」的 1/3 */
  .submit-area {
    display: flex;
    align-items: stretch;
    gap: 10px;
  }
  .submit-btn, .next-btn, .analysis-btn {
    padding: 10px 24px;
    font-size: 15px;
  }
  .submit-btn {
    flex: 3;
  }
  .dont-know-btn {
    flex: 1;
    width: auto;
    padding: 10px 4px;
    font-size: 15px;
    white-space: nowrap;
  }
  .result-btns {
    display: contents;
  }
  .result-btns .analysis-btn,
  .result-btns .next-btn {
    flex: 1;
  }
}
/* 报错按钮 */
.report-btn {
  margin-left: auto;
  flex-shrink: 0;
  background: none;
  border: 1px solid #e0e0e0;
  font-size: 13px;
  color: #999;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 6px;
  transition: all 0.2s;
}

.report-btn:hover {
  background: #fff2f0;
  color: #ff4d4f;
  border-color: #ffccc7;
}

/* 报错弹窗 */
.report-mask {
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
}

.report-modal {
  background: #fff;
  border-radius: 14px;
  width: 90%;
  max-width: 420px;
  max-height: 80vh;
  overflow-y: auto;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.report-header h3 {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.report-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0 8px;
}

.report-body {
  padding: 20px;
}

.report-tip {
  font-size: 14px;
  color: #555;
  margin: 0 0 12px;
}

.report-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.report-option {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #555;
  cursor: pointer;
}

.report-option input {
  width: 16px;
  height: 16px;
}

.report-textarea label {
  display: block;
  font-size: 14px;
  color: #555;
  margin-bottom: 6px;
}

.report-textarea textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  min-height: 80px;
  resize: vertical;
  outline: none;
  box-sizing: border-box;
}

.report-textarea textarea:focus {
  border-color: #4a90d9;
}

.report-footer {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  align-items: center;
}

.report-error {
  color: #ff4d4f;
  font-size: 13px;
  margin-right: auto;
}

.report-cancel {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  background: #fff;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  color: #666;
}

.report-submit {
  padding: 8px 20px;
  background: #4a90d9;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.report-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
