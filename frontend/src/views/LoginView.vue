<template>
  <div class="login-wrap">
    <n-card class="login-card" title="灵工企业风控 Agent 系统">
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
        <n-button type="primary" block :loading="loading" @click="handleLogin">登 录</n-button>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
// 登录页：用户名 / 密码登录，登录成功后跳转到 redirect 或 /chat
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NCard,
  NForm,
  NFormItem,
  NInput,
  NButton,
  useMessage,
  type FormInst,
  type FormRules,
} from 'naive-ui'
import { useAuthStore } from '@/stores/auth'

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
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa, #e4ecf7);
}
.login-card {
  width: 380px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}
</style>
