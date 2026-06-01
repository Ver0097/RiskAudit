<template>
  <div class="msg" :class="role">
    <div class="bubble">
      <span v-if="content">{{ content }}</span>
      <span v-else class="placeholder">…</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ role: 'user' | 'assistant'; content: string }>()
</script>

<style scoped>
.msg {
  display: flex;
  margin: 8px 0;
}
.msg.user { justify-content: flex-end; }
.msg.assistant { justify-content: flex-start; }
.bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 12px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}
.msg.user .bubble { background: #2080f0; color: #fff; }
.msg.assistant .bubble { background: #f0f2f5; color: #1f2329; }
.placeholder { opacity: 0.5; }
</style>
