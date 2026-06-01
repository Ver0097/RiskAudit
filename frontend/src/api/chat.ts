const BASE = import.meta.env.VITE_API_BASE ?? '/api'

export interface StreamHandlers {
  onDelta: (text: string) => void
  onDone?: () => void
  onError?: (msg: string, status?: number) => void
}

/**
 * 调用 /chat/stream（SSE 协议），逐 token 触发 onDelta。
 * 因为需要 POST + 自定义 Header，浏览器原生 EventSource 不适用，改用 fetch + ReadableStream 解析 text/event-stream。
 */
export async function streamChat(
  message: string,
  handlers: StreamHandlers,
  signal?: AbortSignal,
) {
  const token = localStorage.getItem('access_token') ?? ''
  let resp: Response
  try {
    resp = await fetch(`${BASE}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        Accept: 'text/event-stream',
      },
      body: JSON.stringify({ message }),
      signal,
    })
  } catch (e: any) {
    if (e?.name === 'AbortError') return
    handlers.onError?.('网络错误，请稍后重试')
    return
  }

  if (!resp.ok || !resp.body) {
    if (resp.status === 401) {
      // 触发全局 401 处理：清 token，让路由守卫接管
      localStorage.removeItem('access_token')
      handlers.onError?.('登录已失效，请重新登录', 401)
    } else {
      handlers.onError?.(`请求失败：${resp.status}`, resp.status)
    }
    return
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  try {
    while (true) {
      let chunk
      try {
        chunk = await reader.read()
      } catch (e: any) {
        if (e?.name === 'AbortError') return
        handlers.onError?.('流式响应中断')
        return
      }
      const { done, value } = chunk
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      // SSE 帧以空行（\n\n）分割
      const frames = buffer.split('\n\n')
      buffer = frames.pop() ?? ''

      for (const raw of frames) {
        // 跳过注释行（以 : 开头）与空帧
        if (!raw.trim() || raw.trim().startsWith(':')) continue

        let event = 'message'
        const dataLines: string[] = []
        for (const line of raw.split('\n')) {
          if (line.startsWith(':')) continue
          if (line.startsWith('event:')) event = line.slice(6).trim()
          else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim())
        }
        if (dataLines.length === 0) continue
        const payload = dataLines.join('\n')

        if (event === 'message') {
          try {
            const obj = JSON.parse(payload) as { delta?: string }
            if (obj.delta) handlers.onDelta(obj.delta)
          } catch {
            // 忽略非 JSON 帧
          }
        } else if (event === 'done') {
          handlers.onDone?.()
          return
        } else if (event === 'error') {
          try {
            const obj = JSON.parse(payload) as { message?: string }
            handlers.onError?.(obj.message ?? '未知错误')
          } catch {
            handlers.onError?.(payload)
          }
          return
        }
      }
    }
    handlers.onDone?.()
  } finally {
    try {
      reader.releaseLock()
    } catch {
      // 已释放或锁已失效，忽略
    }
  }
}
