<template>
  <div class="msg" :class="role">
    <!-- AI 头像：mini 版的盾牌+节点 logo -->
    <div v-if="role === 'assistant'" class="avatar ai" aria-hidden="true">
      <svg width="20" height="20" viewBox="0 0 32 32" fill="none">
        <defs>
          <linearGradient :id="`msgGrad-${uid}`" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
            <stop offset="0" stop-color="#a5b4fc" />
            <stop offset="1" stop-color="#22d3ee" />
          </linearGradient>
        </defs>
        <path
          d="M16 4 L26 7.5 V16 C26 21.5 16 28 16 28 C16 28 6 21.5 6 16 V7.5 Z"
          stroke="white" stroke-width="1.4" stroke-linejoin="round"
          fill="rgba(255,255,255,0.18)"
        />
        <circle cx="16" cy="15" r="2.4" fill="white" />
      </svg>
    </div>

    <!-- 气泡 -->
    <div class="bubble">
      <span v-if="content" class="content">{{ content }}</span>
      <span v-else class="typing" aria-label="正在输入">
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      </span>
    </div>

    <!-- 用户头像 -->
    <div v-if="role === 'user'" class="avatar user" aria-hidden="true">
      {{ userInitial || 'U' }}
    </div>
  </div>
</template>

<script setup lang="ts">
// 单条消息：assistant 左侧带 logo 头像，user 右侧带首字母头像
import { useId } from 'vue'
withDefaults(
  defineProps<{
    role: 'user' | 'assistant'
    content: string
    userInitial?: string
  }>(),
  { userInitial: 'U' },
)
// 每个消息实例独立的 svg gradient id，避免同页面多实例渲染冲突
const uid = useId()
</script>

<style scoped>
.msg {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin: 20px 0;
}
.msg.user { justify-content: flex-end; }
.msg.assistant { justify-content: flex-start; }

/* ===== 头像 ===== */
.avatar {
  width: 32px; height: 32px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-weight: 600;
  font-size: 12.5px;
  letter-spacing: 0.3px;
  color: #fff;
}
.avatar.ai {
  background: linear-gradient(135deg, #6366f1 0%, #06b6d4 100%);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}
.avatar.user {
  background: linear-gradient(135deg, #475569 0%, #1f2937 100%);
  box-shadow: 0 2px 8px rgba(30, 41, 59, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* ===== 气泡 ===== */
.bubble {
  max-width: 72%;
  padding: 12px 16px;
  border-radius: 14px;
  line-height: 1.65;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-word;
}
.msg.user .bubble {
  background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
  color: #fff;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.15);
}
.msg.assistant .bubble {
  background: #fff;
  color: #1a1d2e;
  border: 1px solid #ebedf3;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(20, 30, 50, 0.04);
}

/* ===== 输入中三点动画 ===== */
.typing {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 0;
}
.typing .dot {
  width: 6px; height: 6px;
  background: #94a3b8;
  border-radius: 50%;
  animation: typing 1.2s ease-in-out infinite;
}
.typing .dot:nth-child(2) { animation-delay: 0.18s; }
.typing .dot:nth-child(3) { animation-delay: 0.36s; }
@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}

@media (max-width: 600px) {
  .bubble { max-width: 80%; }
}
</style>
