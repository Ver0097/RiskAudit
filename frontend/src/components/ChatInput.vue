<template>
  <div class="input-wrap">
    <n-input
      v-model:value="text"
      type="textarea"
      :autosize="{ minRows: 1, maxRows: 6 }"
      placeholder="请输入消息（Enter 发送，Shift+Enter 换行）"
      :disabled="disabled"
      @keydown.enter.exact.prevent="onSend"
    />
    <n-button type="primary" :loading="disabled" :disabled="!canSend" @click="onSend">
      发送
    </n-button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { NInput, NButton } from 'naive-ui'

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
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #eee;
  background: #fff;
}
</style>
