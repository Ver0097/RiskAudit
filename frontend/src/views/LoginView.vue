<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides">
    <div class="login-page">
      <!-- ============== 整页背景图 ============== -->
      <img :src="bgImage" alt="" class="bg-img" />
      <div class="bg-mask" aria-hidden="true"></div>

      <!-- ============== 左侧品牌信息（浮于背景） ============== -->
      <aside class="visual-content">
        <!-- 顶部状态徽章 -->
        <div class="status-bar">
          <span class="status-dot"></span>
          <span>SYSTEM&nbsp;ONLINE · v0.1.0</span>
        </div>

        <!-- 中下部品牌 + 特性 -->
        <div class="visual-bottom">
          <div class="brand-block">
            <span class="brand-logo">
              <svg width="44" height="44" viewBox="0 0 48 48" fill="none">
                <defs>
                  <linearGradient id="visualLogoGrad" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
                    <stop offset="0" stop-color="#a5b4fc" />
                    <stop offset="1" stop-color="#22d3ee" />
                  </linearGradient>
                </defs>
                <path
                  d="M24 4 L40 10 V24 C40 33 24 44 24 44 C24 44 8 33 8 24 V10 Z"
                  stroke="url(#visualLogoGrad)" stroke-width="1.6" stroke-linejoin="round"
                  fill="rgba(165, 180, 252, 0.1)"
                />
                <circle cx="24" cy="22" r="13" stroke="url(#visualLogoGrad)" stroke-width="0.6" opacity="0.35" fill="none" />
                <circle cx="24" cy="22" r="8" stroke="url(#visualLogoGrad)" stroke-width="0.8" opacity="0.6" fill="none" />
                <circle cx="24" cy="22" r="3" fill="url(#visualLogoGrad)" />
              </svg>
            </span>
            <h1 class="brand-name">
              灵工 <span class="brand-mark">RiskAudit</span>
            </h1>
            <p class="brand-tagline">AI 驱动的企业风控决策中枢</p>
          </div>
        </div>
      </aside>

      <!-- ============== 右侧表单区（浮于背景） ============== -->
      <main class="form-side">
        <div class="form-stage">
          <header class="form-head">
            <h2>欢迎登录</h2>
            <p>请使用账号登录以继续访问控制台</p>
          </header>

          <section class="card">
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
        </div>
      </main>
    </div>
  </n-config-provider>
</template>

<script setup lang="ts">
// 登录页：整页背景图 + 左侧品牌信息 + 右侧半透明玻璃态登录卡
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
import bgImage from '@/images/fk.png'

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
    color: 'rgba(15, 23, 42, 0.4)',
    colorFocus: 'rgba(15, 23, 42, 0.55)',
    border: '1px solid rgba(148, 163, 184, 0.22)',
    borderHover: '1px solid rgba(129, 140, 248, 0.6)',
    borderFocus: '1px solid rgba(129, 140, 248, 0.9)',
    boxShadowFocus: '0 0 0 3px rgba(99, 102, 241, 0.2)',
    placeholderColor: 'rgba(203, 213, 225, 0.55)',
    textColor: '#f1f5f9',
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
/* ============== 整页容器 ============== */
.login-page {
  position: relative;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  background: #0a0e27;
  color: #e6e8f0;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
  overflow: hidden;
}

/* ============== 整页背景图 ============== */
.bg-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  z-index: 0;
  /* 让图整体更融入深色调 */
  filter: saturate(1.05);
}
.bg-mask {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background:
    /* 左下角加暗：让品牌文字 + 特性卡可读 */
    linear-gradient(135deg, rgba(10, 14, 39, 0.25) 0%, transparent 35%, rgba(10, 14, 39, 0.55) 100%),
    /* 右侧加深：让表单卡区域偏暗，半透明卡浮起来对比更强 */
    linear-gradient(90deg, transparent 45%, rgba(10, 14, 39, 0.55) 75%, rgba(10, 14, 39, 0.7) 100%),
    /* 整体压暗一档 */
    linear-gradient(180deg, rgba(10, 14, 39, 0.15) 0%, rgba(10, 14, 39, 0.35) 100%);
}

/* ============== 左侧品牌内容 ============== */
.visual-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 40px 48px;
  color: #fff;
}

/* 顶部状态徽章 */
.status-bar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px 5px 10px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.8px;
  color: rgba(255, 255, 255, 0.85);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  font-family: 'SF Mono', 'JetBrains Mono', ui-monospace, Consolas, monospace;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  align-self: flex-start;
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

/* 中下部容器 */
.visual-bottom {
  max-width: 460px;
  animation: fadeUp 0.8s cubic-bezier(0.22, 0.8, 0.36, 1) both;
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 品牌 */
.brand-block {
  margin-bottom: 0;
}
.brand-logo {
  display: inline-flex;
  margin-bottom: 14px;
  filter: drop-shadow(0 4px 16px rgba(99, 102, 241, 0.5));
}
.brand-name {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.6px;
  color: #f1f5f9;
  text-shadow: 0 2px 16px rgba(0, 0, 0, 0.5);
}
.brand-mark {
  background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 40%, #22d3ee 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}
.brand-tagline {
  margin: 8px 0 0;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 0.3px;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.4);
}

/* ============== 右侧表单区 ============== */
.form-side {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  /* 已无独立背景：背景图直接透过来 */
}

.form-stage {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  animation: fadeUp 0.7s cubic-bezier(0.22, 0.8, 0.36, 1) both;
  animation-delay: 0.1s;
}

.form-head {
  margin-bottom: 22px;
}
.form-head h2 {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
}
.form-head p {
  margin: 6px 0 0;
  color: rgba(203, 213, 225, 0.85);
  font-size: 13.5px;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.3);
}

/* ===== 半透明玻璃卡片 ===== */
.card {
  position: relative;
  padding: 28px 26px 22px;
  border-radius: 16px;
  /* 加深 + 加透：让背景图清晰透出 */
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.45) 0%, rgba(15, 23, 42, 0.32) 100%);
  backdrop-filter: blur(28px) saturate(160%);
  -webkit-backdrop-filter: blur(28px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow:
    0 32px 80px rgba(0, 0, 0, 0.55),
    0 2px 6px rgba(0, 0, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.14);
  overflow: hidden;
}
.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 18px;
  right: 18px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.45), transparent);
}

/* Naive UI 标签深度覆盖 */
.card :deep(.n-form-item-label) { padding-bottom: 6px; }
.card :deep(.n-form-item-label__text) {
  color: #e2e8f0;
  font-size: 12.5px;
  letter-spacing: 0.3px;
}

/* 登录按钮 */
.submit {
  margin-top: 6px;
  height: 44px !important;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 4px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
  border: none !important;
  box-shadow:
    0 8px 24px rgba(99, 102, 241, 0.45),
    inset 0 1px 0 rgba(255, 255, 255, 0.28) !important;
  transition: transform 0.25s ease, box-shadow 0.25s ease, filter 0.25s ease;
}
.submit:hover {
  transform: translateY(-1px);
  filter: brightness(1.08);
  box-shadow:
    0 14px 32px rgba(99, 102, 241, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.32) !important;
}
.submit:active { transform: translateY(0); }

.card-foot {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px dashed rgba(148, 163, 184, 0.2);
  text-align: center;
}
.hint {
  font-size: 12px;
  color: rgba(203, 213, 225, 0.65);
}

.page-foot {
  margin-top: 20px;
  text-align: center;
  font-size: 11.5px;
  color: rgba(148, 163, 184, 0.55);
  letter-spacing: 0.4px;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
}

/* ============== 响应式：小屏隐藏左侧文字，表单居中 ============== */
@media (max-width: 960px) {
  .login-page { grid-template-columns: 1fr; }
  .visual-content { display: none; }
  .form-side { padding: 24px; }
  /* 整屏背景蒙版重新平衡：去掉左轻右重，整体均匀加暗 */
  .bg-mask {
    background:
      linear-gradient(180deg, rgba(10, 14, 39, 0.35) 0%, rgba(10, 14, 39, 0.55) 100%);
  }
}

@media (max-width: 480px) {
  .form-stage { max-width: 100%; }
  .card { padding: 22px 20px; }
  .form-head h2 { font-size: 22px; }
}
</style>
