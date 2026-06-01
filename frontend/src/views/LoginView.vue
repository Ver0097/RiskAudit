<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides">
    <div class="login-page">
      <!-- 背景层：网格 + 双色径向光晕 -->
      <div class="bg-grid" aria-hidden="true"></div>
      <div class="bg-glow bg-glow-indigo" aria-hidden="true"></div>
      <div class="bg-glow bg-glow-cyan" aria-hidden="true"></div>

      <!-- 装饰流光线 -->
      <svg class="bg-deco" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <defs>
          <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#6366f1" stop-opacity="0" />
            <stop offset="50%" stop-color="#818cf8" stop-opacity="0.4" />
            <stop offset="100%" stop-color="#06b6d4" stop-opacity="0" />
          </linearGradient>
        </defs>
        <path d="M-50 200 Q 400 150 800 280 T 1300 240" stroke="url(#lineGrad)" stroke-width="1" fill="none" />
        <path d="M-50 600 Q 350 700 750 580 T 1300 620" stroke="url(#lineGrad)" stroke-width="1" fill="none" opacity="0.6" />
      </svg>

      <main class="stage">
        <!-- 顶部状态条 -->
        <div class="status-bar">
          <span class="status-dot"></span>
          <span>SYSTEM&nbsp;ONLINE · v0.1.0</span>
        </div>

        <!-- 品牌区 -->
        <header class="brand">
          <span class="brand-logo">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <defs>
                <linearGradient id="logoGrad" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
                  <stop offset="0" stop-color="#818cf8" />
                  <stop offset="1" stop-color="#06b6d4" />
                </linearGradient>
              </defs>
              <!-- 盾牌外形 -->
              <path
                d="M24 4 L40 10 V24 C40 33 24 44 24 44 C24 44 8 33 8 24 V10 Z"
                stroke="url(#logoGrad)" stroke-width="1.4" stroke-linejoin="round"
                fill="rgba(99,102,241,0.08)"
              />
              <!-- 节点环 -->
              <circle cx="24" cy="22" r="13" stroke="url(#logoGrad)" stroke-width="0.6" opacity="0.35" fill="none" />
              <circle cx="24" cy="22" r="8" stroke="url(#logoGrad)" stroke-width="0.8" opacity="0.6" fill="none" />
              <circle cx="24" cy="22" r="3" fill="url(#logoGrad)" />
              <!-- 上下两个小卫星节点 -->
              <circle cx="24" cy="9" r="1.2" fill="#818cf8" />
              <circle cx="24" cy="35" r="1.2" fill="#06b6d4" />
            </svg>
          </span>
          <h1 class="brand-name">
            灵工 <span class="brand-mark">RiskAudit</span>
          </h1>
          <p class="brand-sub">AI 驱动的企业风控决策中枢</p>
        </header>

        <!-- 登录卡片 -->
        <section class="card">
          <div class="card-head">
            <h2>欢迎回来</h2>
            <p>请使用账号登录以继续访问控制台</p>
          </div>

          <n-form ref="formRef" :model="form" :rules="rules" label-placement="top" @submit.prevent>
            <n-form-item label="用户名" path="username">
              <n-input v-model:value="form.username" placeholder="请输入用户名" autofocus />
            </n-form-item>
            <n-form-item label="密码" path="password">
              <n-input
                v-model:value="form.password"
                type="password"
                show-password-on="click"
                placeholder="请输入密码"
                @keyup.enter="handleLogin"
              />
            </n-form-item>
            <n-button type="primary" block :loading="loading" @click="handleLogin" class="submit">
              登 录
            </n-button>
          </n-form>

          <div class="card-foot">
            <span class="hint">遇到问题请联系系统管理员</span>
          </div>
        </section>

        <footer class="page-foot">
          © 2026 灵工 · 内部系统 · 仅限授权人员访问
        </footer>
      </main>
    </div>
  </n-config-provider>
</template>

<script setup lang="ts">
// 登录页：用户名 / 密码登录，登录成功后跳转到 redirect 或 /chat
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NConfigProvider,
  NForm,
  NFormItem,
  NInput,
  NButton,
  darkTheme,
  useMessage,
  type FormInst,
  type FormRules,
  type GlobalThemeOverrides,
} from 'naive-ui'
import { useAuthStore } from '@/stores/auth'

// 局部主题覆盖：仅作用于登录页内部的 naive-ui 组件
const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#6366f1',
    primaryColorHover: '#818cf8',
    primaryColorPressed: '#4f46e5',
    primaryColorSuppl: '#6366f1',
    borderRadius: '10px',
  },
  Input: {
    color: 'rgba(15, 23, 42, 0.45)',
    colorFocus: 'rgba(15, 23, 42, 0.65)',
    border: '1px solid rgba(148, 163, 184, 0.18)',
    borderHover: '1px solid rgba(129, 140, 248, 0.6)',
    borderFocus: '1px solid rgba(129, 140, 248, 0.9)',
    boxShadowFocus: '0 0 0 3px rgba(99, 102, 241, 0.18)',
    placeholderColor: 'rgba(148, 163, 184, 0.55)',
    textColor: '#e2e8f0',
    heightMedium: '42px',
  },
}

const form = reactive({ username: '', password: '' })
const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const formRef = ref<FormInst | null>(null)
const loading = ref(false)
const message = useMessage()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

// 登录提交：校验 -> 调用 store.login -> 跳转
async function handleLogin() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    await auth.login(form.username.trim(), form.password)
    message.success('登录成功')
    const redirect = (route.query.redirect as string) || '/chat'
    router.replace(redirect)
  } catch (e: any) {
    const msg = e?.response?.data?.detail ?? '登录失败，请重试'
    message.error(typeof msg === 'string' ? msg : '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ===== 整页容器 ===== */
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  overflow: hidden;
  color: #e6e8f0;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
  background:
    radial-gradient(ellipse 80% 60% at 20% 10%, rgba(99, 102, 241, 0.18) 0%, transparent 60%),
    radial-gradient(ellipse 70% 50% at 80% 90%, rgba(6, 182, 212, 0.12) 0%, transparent 60%),
    linear-gradient(135deg, #0a0e27 0%, #0b0f24 50%, #060818 100%);
}

/* ===== 背景层 ===== */
.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
  pointer-events: none;
}
.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  pointer-events: none;
}
.bg-glow-indigo {
  width: 520px;
  height: 520px;
  top: -160px;
  left: -120px;
  background: rgba(99, 102, 241, 0.55);
  opacity: 0.5;
}
.bg-glow-cyan {
  width: 600px;
  height: 600px;
  bottom: -220px;
  right: -160px;
  background: rgba(6, 182, 212, 0.4);
  opacity: 0.45;
}
.bg-deco {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.7;
}

/* ===== 主舞台 ===== */
.stage {
  position: relative;
  width: 100%;
  max-width: 440px;
  z-index: 1;
  animation: fadeUp 0.7s cubic-bezier(0.22, 0.8, 0.36, 1) both;
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ===== 顶部状态条 ===== */
.status-bar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px 5px 10px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.8px;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 999px;
  margin-bottom: 24px;
  font-family: 'SF Mono', 'JetBrains Mono', ui-monospace, Consolas, monospace;
}
.status-dot {
  width: 6px;
  height: 6px;
  background: #22c55e;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.8), 0 0 2px #22c55e;
  animation: pulse 2.2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.45; transform: scale(0.85); }
}

/* ===== 品牌区 ===== */
.brand {
  margin-bottom: 28px;
}
.brand-logo {
  display: inline-flex;
  margin-bottom: 14px;
  filter: drop-shadow(0 4px 16px rgba(99, 102, 241, 0.4));
}
.brand-name {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.5px;
  color: #f1f5f9;
}
.brand-mark {
  background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 40%, #22d3ee 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  font-weight: 700;
}
.brand-sub {
  margin: 6px 0 0;
  color: #94a3b8;
  font-size: 13px;
  letter-spacing: 0.3px;
}

/* ===== 玻璃态卡片 ===== */
.card {
  position: relative;
  padding: 30px 28px 26px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.045) 0%, rgba(255, 255, 255, 0.02) 100%);
  backdrop-filter: blur(24px) saturate(140%);
  -webkit-backdrop-filter: blur(24px) saturate(140%);
  border: 1px solid rgba(255, 255, 255, 0.07);
  box-shadow:
    0 24px 60px rgba(0, 0, 0, 0.45),
    0 2px 4px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  overflow: hidden;
}
/* 顶部 1px 高亮线（液态玻璃质感） */
.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 18px;
  right: 18px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
}

.card-head {
  margin-bottom: 22px;
}
.card-head h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #f1f5f9;
  letter-spacing: -0.2px;
}
.card-head p {
  margin: 6px 0 0;
  color: #94a3b8;
  font-size: 13px;
}

/* Naive UI 标签深度覆盖 */
.card :deep(.n-form-item-label) {
  padding-bottom: 6px;
}
.card :deep(.n-form-item-label__text) {
  color: #cbd5e1;
  font-size: 12.5px;
  letter-spacing: 0.3px;
}

/* 登录按钮：蓝紫渐变 */
.submit {
  margin-top: 6px;
  height: 44px !important;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 4px;
  --n-color: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
  border: none !important;
  box-shadow:
    0 8px 24px rgba(99, 102, 241, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
  transition: transform 0.25s ease, box-shadow 0.25s ease, filter 0.25s ease;
}
.submit:hover {
  transform: translateY(-1px);
  filter: brightness(1.08);
  box-shadow:
    0 14px 32px rgba(99, 102, 241, 0.55),
    inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
}
.submit:active {
  transform: translateY(0);
}

.card-foot {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px dashed rgba(148, 163, 184, 0.15);
  text-align: center;
}
.hint {
  font-size: 12px;
  color: #64748b;
}

/* 页脚 */
.page-foot {
  margin-top: 24px;
  text-align: center;
  font-size: 11.5px;
  color: #475569;
  letter-spacing: 0.4px;
}

/* 小屏适配 */
@media (max-width: 480px) {
  .stage { max-width: 100%; }
  .card { padding: 24px 20px; }
  .brand-name { font-size: 24px; }
}
</style>
