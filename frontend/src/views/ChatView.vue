<template>
  <div class="chat-shell">
    <header class="chat-header">
      <span class="title">灵工企业风控 Agent 系统</span>
      <n-space :size="12" align="center">
        <span v-if="auth.user" class="user">{{ auth.user.display_name || auth.user.username }}</span>
        <n-button quaternary size="small" @click="onLogout">退出登录</n-button>
      </n-space>
    </header>

    <main class="chat-body" ref="bodyRef">
      <ChatMessage
        v-for="(m, i) in messages"
        :key="i"
        :role="m.role"
        :content="m.content"
      />
    </main>

    <ChatInput :disabled="sending" @send="onSend" />
  </div>
</template>

<script setup lang="ts">
import { nextTick, onUnmounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NSpace, useMessage } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import ChatMessage from '@/components/ChatMessage.vue'
import ChatInput from '@/components/ChatInput.vue'
import { streamChat } from '@/api/chat'

interface Msg { role: 'user' | 'assistant'; content: string }

const auth = useAuthStore()
const router = useRouter()
const message = useMessage()

const messages = reactive<Msg[]>([])
const sending = ref(false)
const abortCtrl = ref<AbortController | null>(null)
const bodyRef = ref<HTMLElement | null>(null)

async function onSend(text: string) {
  const assistantMsg = reactive<Msg>({ role: 'assistant', content: '' })
  messages.push({ role: 'user', content: text })
  messages.push(assistantMsg)
  await scrollToBottom()

  sending.value = true
  abortCtrl.value?.abort()
  const ctrl = new AbortController()
  abortCtrl.value = ctrl

  try {
    await streamChat(
      text,
      {
        onDelta: (piece) => {
          assistantMsg.content += piece
          scrollToBottom()
        },
        onError: (m) => {
          message.error(m)
          assistantMsg.content = assistantMsg.content || `（请求失败：${m}）`
        },
      },
      ctrl.signal,
    )
  } finally {
    sending.value = false
    if (abortCtrl.value === ctrl) abortCtrl.value = null
    await scrollToBottom()
  }
}

async function onLogout() {
  abortCtrl.value?.abort()
  await auth.logout()
  message.success('已退出')
  router.replace('/login')
}

onUnmounted(() => abortCtrl.value?.abort())

async function scrollToBottom() {
  await nextTick()
  const el = bodyRef.value
  if (el) el.scrollTop = el.scrollHeight
}
</script>

<style scoped>
.chat-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fafafa;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #eee;
}
.chat-header .title { font-weight: 600; font-size: 16px; }
.chat-header .user { color: #666; font-size: 13px; }
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}
</style>
