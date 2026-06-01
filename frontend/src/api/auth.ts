import { http } from './http'

// 用户信息：与后端 UserOut schema 对应
export interface UserOut {
  id: number
  username: string
  display_name: string
  is_admin: boolean
  created_at: string
}

// 后端登录响应：access_token / token_type / expires_in
export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// 登录：OAuth2 password grant 风格，使用表单编码
export async function login(username: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams()
  body.set('username', username)
  body.set('password', password)
  const { data } = await http.post<TokenResponse>('/auth/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

// 登出：把当前 token 加入黑名单
export async function logout(): Promise<void> {
  await http.post('/auth/logout')
}

// 获取当前登录用户信息
export async function me(): Promise<UserOut> {
  const { data } = await http.get<UserOut>('/auth/me')
  return data
}
