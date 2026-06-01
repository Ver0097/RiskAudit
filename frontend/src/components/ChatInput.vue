<template>
  <div class="input-wrap">
    <n-input
      v-model:value="text"
      type="textarea"
      :autosize="{ minRows: 1, maxRows: 6 }"
      placeholder="请输入消息（Enter 发送，Shift+Enter 换行）"
      :disabled="disabled"
      :bordered="false"
      class="input-box"
      @keydown.enter.exact.prevent="onSend"
    />
    <button
      class="send-btn"
      :class="{ active: canSend, loading: disabled }"
      :disabled="!canSend"
      :title="canSend ? '发送 (Enter)' : '请先输入内容'"
      @click="onSend"
    >
      <svg v-if="!disabled" width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M2 8L14 2L9 14L7.5 9L2 8Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" fill="currentColor" />
      </svg>
      <span v-else class="spinner"></span>
    </button>
  </div>
</template>

<script setup lang="ts">
// 输入栏：单文本框 + 圆形发送按钮，融入外部卡片容器
import { computed, ref } from 'vue'
import { NInput } from 'naive-ui'

const props = defineProps<{ disabled: boolean }>()
const emit = defineEmits<{ (e: 'send', text: string): void }>()

const text = ref('')
const canSend = computed(() => text.value.trim().length > 0 && !props.disabled)

function onSend() {
  if (!canSend.value) return
  const t = text.value.trim()
  text.value = ''
  emit('send', t)
}
</script>

<style scoped>
.input-wrap {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 8px 10px 10px 16px;
  background: transparent;
}

/* 让 naive-ui textarea 去掉默认背景/边框，看起来像外层卡片的一部分 */
.input-box :deep(.n-input__textarea-el) {
  font-size: 14px;
  line-height: 1.55;
  color: #1a1d2e;
  padding: 8px 0;
}
.input-box :deep(.n-input__textarea-el)::placeholder {
  color: #94a3b8;
}
.input-box :deep(.n-input) {
  background: transparent;
}
.input-box :deep(.n-input-wrapper) {
  padding: 0;
}

/* 发送按钮：默认灰、可发送时蓝紫渐变、加载时旋转 */
.send-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  background: #eef0f5;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: not-allowed;
  transition: background 0.18s, color 0.18s, transform 0.15s, box-shadow 0.2s;
}
.send-btn.active {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}
.send-btn.active:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.45);
}
.send-btn.active:active { transform: translateY(0); }
.send-btn.loading {
  background: linear-gradient(135deg, #818cf8 0%, #a5b4fc 100%);
  color: #fff;
  cursor: wait;
}

.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
