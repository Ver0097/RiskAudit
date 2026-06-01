import axios, { AxiosError, type AxiosInstance } from 'axios'

// 后端 API 基础路径，默认走 Vite 代理的 /api
const BASE = import.meta.env.VITE_API_BASE ?? '/api'

// 全局共享的 axios 实例
export const http: AxiosInstance = axios.create({
  baseURL: BASE,
  timeout: 30000,
})

// 请求拦截：自动附加 Bearer Token
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }
  return config
})

// 响应拦截：401 时清理本地凭据并跳转登录页
http.interceptors.response.use(
  (resp) => resp,
  (err: AxiosError) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      // 避免循环：仅在非登录页时跳转
      if (location.pathname !== '/login') {
        location.replace('/login')
      }
    }
    return Promise.reject(err)
  },
)
