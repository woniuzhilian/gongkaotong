<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <span class="result-tag" :class="isCorrect ? 'correct' : 'wrong'">
          {{ isCorrect ? '回答正确' : '回答错误' }}
        </span>
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
          <div class="analysis-content" v-html="renderedAnalysis"></div>
        </div>
      </div>

      <div class="modal-footer">
        <div class="footer-btns">
          <button
            class="knowledge-btn"
            :class="{ disabled: !hasKnowledge }"
            :disabled="!hasKnowledge"
            :title="hasKnowledge ? '查看本题考查的知识点扩展' : '计算题暂无知识点扩展'"
            @click="showKnowledge = true"
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
import katex from 'katex'
import knowledgeExt from '../data/knowledgeExt.json'

const props = defineProps({
  visible: { type: Boolean, default: false },
  question: { type: Object, required: true },
  userAnswer: { type: String, default: '' },
  isLast: { type: Boolean, default: false }
})

defineEmits(['close', 'next'])

const showKnowledge = ref(false)

// 切题时自动关闭知识点弹窗
watch(() => props.question, () => { showKnowledge.value = false })

const isCorrect = computed(() => props.userAnswer === props.question.answer)

// 知识点扩展：仅概念题可用；优先按题目id匹配，其次按「大科目|小科目」兜底
const knowledgeHtml = computed(() => {
  const q = props.question
  if (!q || q.qtype !== 'concept') return ''
  return knowledgeExt['q:' + q.id] || knowledgeExt[q.bigSubject + '|' + q.smallSubject] || ''
})
const hasKnowledge = computed(() => !!knowledgeHtml.value)

const renderedKnowledge = computed(() => renderLatex(knowledgeHtml.value))

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
  font-size: 14px;
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
  font-size: 14.5px;
  line-height: 1.8;
  color: #444;
  word-break: break-word;
}

.knowledge-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0;
  font-size: 13.5px;
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
