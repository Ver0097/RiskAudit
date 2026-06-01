import { defineStore } from 'pinia'
import * as authApi from '@/api/auth'

interface State {
  token: string | null
  user: authApi.UserOut | null
}

// 全局认证状态：token + 用户信息
export const useAuthStore = defineStore('auth', {
  state: (): State => ({
    // 启动时从 localStorage 恢复 token
    token: localStorage.getItem('access_token'),
    user: null,
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
  },
  actions: {
    // 登录：保存 token 后拉取用户信息
    async login(username: string, password: string) {
      const tk = await authApi.login(username, password)
      this.token = tk.access_token
      localStorage.setItem('access_token', tk.access_token)
      await this.fetchMe()
    },
    // 拉取当前用户信息
    async fetchMe() {
      this.user = await authApi.me()
    },
    // 登出：即使后端报错也要清本地
    async logout() {
      try {
        await authApi.logout()
      } catch (_) {
        // 忽略后端失败，保证本地状态被清理
      }
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
    },
  },
})
