<template>
  <div class="app-shell">
    <!-- ============== 左侧 Sidebar ============== -->
    <aside class="sidebar">
      <!-- 品牌区 -->
      <div class="brand">
        <span class="brand-logo">
          <svg width="30" height="30" viewBox="0 0 32 32" fill="none">
            <defs>
              <linearGradient id="navLogoGrad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                <stop offset="0" stop-color="#818cf8" />
                <stop offset="1" stop-color="#06b6d4" />
              </linearGradient>
            </defs>
            <path
              d="M16 3 L27 7 V16 C27 22 16 29 16 29 C16 29 5 22 5 16 V7 Z"
              stroke="url(#navLogoGrad)" stroke-width="1.4" stroke-linejoin="round"
              fill="rgba(99,102,241,0.12)"
            />
            <circle cx="16" cy="15" r="5" stroke="url(#navLogoGrad)" stroke-width="0.6" opacity="0.5" fill="none" />
            <circle cx="16" cy="15" r="2.2" fill="url(#navLogoGrad)" />
          </svg>
        </span>
        <div class="brand-text">
          <div class="brand-name">灵工 <span class="brand-mark">RiskAudit</span></div>
          <div class="brand-sub">v0.1.0</div>
        </div>
      </div>

      <!-- 新建对话按钮 -->
      <button class="new-chat" @click="onNewChat">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M7 1.5v11M1.5 7h11" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
        </svg>
        <span>新建对话</span>
      </button>

      <!-- 历史对话列表 -->
      <div class="nav-section history-section">
        <div class="nav-title">最近对话</div>
        <div class="history-list" v-if="conversations.length">
          <button
            v-for="c in conversations"
            :key="c.id"
            class="history-item"
            :class="{ active: c.id === currentId }"
            :title="c.title"
            @click="switchConversation(c.id)"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path
                d="M2 4.5C2 3.4 2.9 2.5 4 2.5h6c1.1 0 2 0.9 2 2v3c0 1.1-0.9 2-2 2H7l-2.5 2v-2H4c-1.1 0-2-0.9-2-2v-3z"
                stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"
              />
            </svg>
            <span class="history-label">{{ c.title }}</span>
          </button>
        </div>
        <div v-else class="empty-history">还没有对话</div>
      </div>

      <!-- 工作台 -->
      <nav class="nav-section">
        <div class="nav-title">工作台</div>
        <a class="nav-item active" href="javascript:;">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <path
              d="M2.5 4.5C2.5 3.4 3.4 2.5 4.5 2.5h7c1.1 0 2 0.9 2 2v4c0 1.1-0.9 2-2 2H8l-3 2.5v-2.5h-0.5c-1.1 0-2-0.9-2-2v-4z"
              stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"
            />
          </svg>
          <span>智能对话</span>
        </a>
        <a class="nav-item disabled" @click.prevent="hintComing">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <path d="M8 1.5l5 1.5v5c0 3-5 6.5-5 6.5S3 11 3 8V3l5-1.5z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" />
          </svg>
          <span>风险审核</span>
          <span class="badge">即将上线</span>
        </a>
        <a class="nav-item disabled" @click.prevent="hintComing">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.3" />
            <path d="M8 2v1.5M8 12.5V14M14 8h-1.5M3.5 8H2M12.2 3.8l-1.1 1.1M4.9 11.1l-1.1 1.1M12.2 12.2l-1.1-1.1M4.9 4.9L3.8 3.8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" />
          </svg>
          <span>规则配置</span>
        </a>
      </nav>

      <!-- 数据 -->
      <nav class="nav-section">
        <div class="nav-title">数据</div>
        <a class="nav-item disabled" @click.prevent="hintComing">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <path d="M2 14h12M4 14V8.5M8 14V3.5M12 14V10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <span>报表中心</span>
        </a>
      </nav>

      <!-- 底部用户卡 -->
      <div class="user-bar">
        <div class="avatar">{{ initials }}</div>
        <div class="user-meta">
          <div class="user-name">{{ displayName }}</div>
          <div class="user-role">{{ auth.user?.is_admin ? '管理员' : '用户' }}</div>
        </div>
        <button class="logout-btn" title="退出登录" @click="onLogout">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M10 11l3-3-3-3M13 8H6M9 14H3c-0.6 0-1-0.4-1-1V3c0-0.6 0.4-1 1-1h6"
              stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"
            />
          </svg>
        </button>
      </div>
    </aside>

    <!-- ============== 主区 ============== -->
    <main class="main">
      <header class="toolbar">
        <div class="toolbar-left">
          <h1 class="page-title">{{ currentConv?.title || '智能对话' }}</h1>
          <span class="model-tag">
            <span class="dot"></span>
            DeepSeek-V3
          </span>
        </div>
        <div class="toolbar-right">
          <button class="ghost-btn" :disabled="!currentMessages.length" @click="onClearChat">
            清空对话
          </button>
        </div>
      </header>

      <div class="conversation" ref="bodyRef">
        <div class="conversation-inner">
          <!-- 空状态：欢迎 + 示例 prompts -->
          <div v-if="!currentMessages.length" class="empty-state">
            <div class="hello-mark">
              <svg width="44" height="44" viewBox="0 0 40 40" fill="none">
                <defs>
                  <linearGradient id="helloGrad" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                    <stop offset="0" stop-color="#6366f1" />
                    <stop offset="1" stop-color="#06b6d4" />
                  </linearGradient>
                </defs>
                <circle cx="20" cy="20" r="18" stroke="url(#helloGrad)" stroke-width="1" opacity="0.25" fill="none" />
                <circle cx="20" cy="20" r="12" stroke="url(#helloGrad)" stroke-width="1" opacity="0.5" fill="none" />
                <circle cx="20" cy="20" r="6" fill="url(#helloGrad)" />
              </svg>
            </div>
            <h2 class="hello-title">你好，{{ displayName }}</h2>
            <p class="hello-sub">我可以帮你解读风控规则、分析数据指标、审核业务案件</p>
            <div class="prompt-chips">
              <button
                v-for="p in samplePrompts"
                :key="p"
                class="chip"
                :disabled="sending"
                @click="onSend(p)"
              >
                <span>{{ p }}</span>
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M2 6h8M6 2l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>
            </div>
          </div>

          <!-- 消息流 -->
          <ChatMessage
            v-for="(m, i) in currentMessages"
            :key="`${currentId}-${i}`"
            :role="m.role"
            :content="m.content"
            :user-initial="initials"
          />
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-area">
        <div class="input-card">
          <ChatInput :disabled="sending" @send="onSend" />
        </div>
        <div class="input-tip">回复内容由 AI 生成，仅供参考</div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// 聊天页：左 sidebar 导航 + 历史对话 + 用户卡，右主区对话流
import { computed, nextTick, onUnmounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import ChatMessage from '@/components/ChatMessage.vue'
import ChatInput from '@/components/ChatInput.vue'
import { streamChat } from '@/api/chat'

interface Msg { role: 'user' | 'assistant'; content: string }
interface Conversation {
  id: string
  title: string
  messages: Msg[]
  createdAt: number
}

const auth = useAuthStore()
const router = useRouter()
const message = useMessage()

// 本地会话状态：后端尚未实现持久化，先放在本地，刷新即丢
const conversations = reactive<Conversation[]>([])
const currentId = ref<string>('')
const sending = ref(false)
const abortCtrl = ref<AbortController | null>(null)
const bodyRef = ref<HTMLElement | null>(null)

const currentConv = computed(() => conversations.find((c) => c.id === currentId.value) ?? null)
const currentMessages = computed(() => currentConv.value?.messages ?? [])

const displayName = computed(() => auth.user?.display_name || auth.user?.username || '访客')
const initials = computed(() => {
  const n = displayName.value
  return n ? n.slice(0, 1).toUpperCase() : 'U'
})

// 示例问题：风控 + AI 相关的引导话题
const samplePrompts = [
  '介绍一下灵工风控 Agent 的主要能力',
  '什么是企业风控的"三道防线"？',
  '给我一段反洗钱（AML）规则的伪代码',
  '总结当前主流欺诈识别的常见维度',
]

function genId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `c_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

// 新建对话：取消正在进行的流，插入一条新会话并选中
function onNewChat() {
  abortCtrl.value?.abort()
  const conv: Conversation = {
    id: genId(),
    title: '新对话',
    messages: reactive<Msg[]>([]),
    createdAt: Date.now(),
  }
  conversations.unshift(conv)
  currentId.value = conv.id
}

// 切换历史会话
function switchConversation(id: string) {
  if (id === currentId.value) return
  abortCtrl.value?.abort()
  currentId.value = id
}

// 清空当前对话内容
function onClearChat() {
  if (!currentConv.value) return
  abortCtrl.value?.abort()
  currentConv.value.messages.splice(0)
  currentConv.value.title = '新对话'
}

// 发送消息：必要时先建会话，第一句话作为对话标题
async function onSend(text: string) {
  if (!currentConv.value) onNewChat()
  const conv = currentConv.value!

  if (conv.messages.length === 0) {
    conv.title = text.length > 18 ? text.slice(0, 18) + '…' : text
  }

  const assistantMsg = reactive<Msg>({ role: 'assistant', content: '' })
  conv.messages.push({ role: 'user', content: text })
  conv.messages.push(assistantMsg)
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

function hintComing() {
  message.info('该模块开发中，敬请期待')
}

onUnmounted(() => abortCtrl.value?.abort())

async function scrollToBottom() {
  await nextTick()
  const el = bodyRef.value
  if (el) el.scrollTop = el.scrollHeight
}

// 进入页面默认创建一个空对话，让用户直接进入欢迎态
onNewChat()
</script>

<style scoped>
/* ============== 全局壳 ============== */
.app-shell {
  display: flex;
  height: 100vh;
  background: #f6f7fb;
  color: #1a1d2e;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
  overflow: hidden;
}

/* ============== 左侧 Sidebar ============== */
.sidebar {
  position: relative;
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  color: #cbd5e1;
  background: linear-gradient(180deg, #0a0e27 0%, #0b1024 50%, #060818 100%);
}
.sidebar::after {
  content: '';
  position: absolute;
  top: 0; right: 0; bottom: 0;
  width: 1px;
  background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.07) 20%, rgba(255, 255, 255, 0.07) 80%, transparent);
  pointer-events: none;
}

/* 品牌 */
.brand {
  display: flex; align-items: center; gap: 10px;
  padding: 18px 18px 14px;
}
.brand-logo {
  display: inline-flex;
  filter: drop-shadow(0 2px 8px rgba(99, 102, 241, 0.4));
}
.brand-text { line-height: 1.1; }
.brand-name {
  font-size: 15px;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.2px;
}
.brand-mark {
  background: linear-gradient(135deg, #a5b4fc, #22d3ee);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.brand-sub {
  font-size: 10.5px;
  color: #64748b;
  font-family: 'SF Mono', 'JetBrains Mono', ui-monospace, monospace;
  letter-spacing: 0.6px;
  margin-top: 3px;
}

/* 新建对话按钮 */
.new-chat {
  display: flex; align-items: center; gap: 8px; justify-content: center;
  margin: 0 14px 14px;
  padding: 9px 14px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: filter 0.2s, transform 0.15s, box-shadow 0.2s;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}
.new-chat:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(99, 102, 241, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.25);
}

/* 通用 section */
.nav-section {
  padding: 0 8px;
  margin-bottom: 14px;
}
.nav-title {
  padding: 8px 10px 6px;
  font-size: 10.5px;
  font-weight: 600;
  color: #475569;
  letter-spacing: 1.2px;
  text-transform: uppercase;
}

/* 历史会话区：撑满中间，可滚动 */
.history-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.history-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 2px;
}
.history-list::-webkit-scrollbar { width: 4px; }
.history-list::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.08); border-radius: 2px; }
.history-list::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.16); }
.empty-history {
  padding: 4px 12px 8px;
  font-size: 11.5px;
  color: #475569;
}

/* 列表项（history & nav 共用） */
.history-item, .nav-item {
  position: relative;
  display: flex; align-items: center; gap: 10px;
  width: 100%;
  padding: 7px 10px;
  margin-bottom: 2px;
  background: transparent;
  color: #94a3b8;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  text-align: left;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.history-item:hover, .nav-item:not(.disabled):hover {
  background: rgba(255, 255, 255, 0.04);
  color: #e2e8f0;
}
.history-item.active, .nav-item.active {
  background: rgba(99, 102, 241, 0.16);
  color: #f1f5f9;
}
.history-item.active::before, .nav-item.active::before {
  content: '';
  position: absolute;
  left: 0; top: 25%; bottom: 25%;
  width: 2px;
  border-radius: 2px;
  background: linear-gradient(180deg, #818cf8, #22d3ee);
}
.history-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.nav-item.disabled {
  color: #475569;
  cursor: not-allowed;
}
.nav-item.disabled:hover { background: transparent; color: #475569; }

.badge {
  margin-left: auto;
  font-size: 9.5px;
  padding: 2px 6px;
  background: rgba(99, 102, 241, 0.18);
  color: #a5b4fc;
  border-radius: 4px;
  font-weight: 600;
  letter-spacing: 0.4px;
}

/* 底部用户卡 */
.user-bar {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.avatar {
  width: 32px; height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1, #06b6d4);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.5px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(99, 102, 241, 0.3);
}
.user-meta { flex: 1; min-width: 0; }
.user-name {
  font-size: 13px;
  font-weight: 600;
  color: #f1f5f9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.user-role {
  font-size: 11px;
  color: #64748b;
  margin-top: 1px;
}
.logout-btn {
  background: transparent;
  border: none;
  color: #64748b;
  padding: 6px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  transition: background 0.15s, color 0.15s;
}
.logout-btn:hover { background: rgba(255, 255, 255, 0.06); color: #f87171; }

/* ============== 主区 ============== */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #f6f7fb;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 28px;
  background: #fff;
  border-bottom: 1px solid #ebedf3;
}
.toolbar-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
.page-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1d2e;
  letter-spacing: -0.2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 480px;
}
.model-tag {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 3px 9px;
  font-size: 11px;
  font-weight: 500;
  font-family: 'SF Mono', 'JetBrains Mono', ui-monospace, monospace;
  background: rgba(99, 102, 241, 0.08);
  color: #6366f1;
  border-radius: 999px;
  letter-spacing: 0.3px;
  flex-shrink: 0;
}
.model-tag .dot {
  width: 5px; height: 5px;
  background: #22c55e;
  border-radius: 50%;
  box-shadow: 0 0 4px #22c55e;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

.ghost-btn {
  padding: 6px 12px;
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e6ee;
  border-radius: 8px;
  font-size: 12.5px;
  cursor: pointer;
  transition: all 0.15s;
}
.ghost-btn:hover:not(:disabled) {
  border-color: #cbd5e1;
  color: #334155;
  background: #f8f9fc;
}
.ghost-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.conversation {
  flex: 1;
  overflow-y: auto;
  scroll-behavior: smooth;
}
.conversation::-webkit-scrollbar { width: 8px; }
.conversation::-webkit-scrollbar-thumb { background: #d8dde6; border-radius: 4px; }
.conversation::-webkit-scrollbar-thumb:hover { background: #c1c8d4; }

.conversation-inner {
  max-width: 780px;
  margin: 0 auto;
  padding: 28px 24px 16px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 16px 20px;
}
.hello-mark {
  display: inline-flex;
  margin-bottom: 16px;
  filter: drop-shadow(0 6px 24px rgba(99, 102, 241, 0.25));
}
.hello-title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #1a1d2e 0%, #4b5563 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}
.hello-sub {
  margin: 8px 0 28px;
  color: #64748b;
  font-size: 14px;
}
.prompt-chips {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 10px;
  max-width: 640px;
  margin: 0 auto;
}
.chip {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 12px 14px;
  background: #fff;
  border: 1px solid #e7eaf2;
  border-radius: 12px;
  color: #475569;
  font-size: 13px;
  cursor: pointer;
  text-align: left;
  line-height: 1.45;
  transition: all 0.18s;
}
.chip svg {
  color: #94a3b8;
  flex-shrink: 0;
  transition: transform 0.18s, color 0.18s;
}
.chip:hover:not(:disabled) {
  border-color: #c7d2fe;
  background: linear-gradient(180deg, #fff, #f7f8ff);
  color: #1a1d2e;
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.08);
  transform: translateY(-1px);
}
.chip:hover:not(:disabled) svg { color: #6366f1; transform: translateX(2px); }
.chip:disabled { opacity: 0.5; cursor: not-allowed; }

/* 输入区 */
.input-area {
  padding: 8px 24px 16px;
}
.input-card {
  max-width: 780px;
  margin: 0 auto;
  background: #fff;
  border: 1px solid #e7eaf2;
  border-radius: 14px;
  box-shadow: 0 4px 16px rgba(20, 30, 50, 0.04);
  overflow: hidden;
  transition: border-color 0.18s, box-shadow 0.18s;
}
.input-card:focus-within {
  border-color: #c7d2fe;
  box-shadow: 0 8px 22px rgba(99, 102, 241, 0.1);
}
.input-tip {
  max-width: 780px;
  margin: 8px auto 0;
  text-align: center;
  font-size: 11px;
  color: #94a3b8;
}

/* 小屏适配：sidebar 收窄 */
@media (max-width: 900px) {
  .sidebar { width: 220px; }
  .brand-name { font-size: 14px; }
  .conversation-inner { padding: 20px 16px 12px; }
  .toolbar { padding: 12px 18px; }
  .input-area { padding: 8px 16px 14px; }
}
</style>
