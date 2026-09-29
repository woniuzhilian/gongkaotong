// Service Worker - PWA 离线缓存
const CACHE_NAME = 'gongkaotong-v1'
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
]

// 安装时缓存核心资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS)
    })
  )
  self.skipWaiting()
})

// 激活时清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    })
  )
  self.clients.claim()
})

// 网络优先，失败时用缓存（保证在线时是最新数据）
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return

  // 只缓存同源请求，不缓存 Supabase API
  const url = new URL(event.request.url)
  if (url.origin !== location.origin) return

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // 成功就缓存一份
        if (response.status === 200) {
          const clone = response.clone()
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clone)
          })
        }
        return response
      })
      .catch(() => {
        // 离线就用缓存
        return caches.match(event.request).then((cached) => {
          if (cached) return cached
          // 都没有就返回首页
          if (event.request.mode === 'navigate') {
            return caches.match('/index.html')
          }
        })
      })
  )
})
