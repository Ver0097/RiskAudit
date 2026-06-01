import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 路由表：登录页为公开页，其余受保护
const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/chat' },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('@/views/ChatView.vue'),
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局守卫：未登录跳转登录页；首次进入受保护页时拉取用户信息
router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const isPublic = to.meta.public === true

  if (isPublic) {
    return true
  }
  if (!auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  // 首次进入受保护页时拉取用户信息
  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      return { name: 'login' }
    }
  }
  return true
})
