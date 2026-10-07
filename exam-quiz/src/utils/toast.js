// 全局轻提示（toast）：非阻塞、自动消失，不影响用户操作
let timer = null

// 注入一次全局样式
if (typeof document !== 'undefined' && !document.querySelector('#toast-style')) {
  const style = document.createElement('style')
  style.id = 'toast-style'
  style.textContent = `
.global-toast {
  position: fixed;
  top: 18%;
  left: 50%;
  transform: translateX(-50%) translateY(-8px);
  background: rgba(0, 0, 0, 0.78);
  color: #fff;
  font-size: 14px;
  padding: 10px 22px;
  border-radius: 22px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  z-index: 99999;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.25s ease, transform 0.25s ease;
  max-width: 80vw;
  text-align: center;
  line-height: 1.5;
}
.global-toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
`
  document.head.appendChild(style)
}

export function showToast(text, duration = 1000) {
  // 复用已有 toast，避免堆叠
  let el = document.querySelector('.global-toast')
  if (!el) {
    el = document.createElement('div')
    el.className = 'global-toast'
    document.body.appendChild(el)
  }
  el.textContent = text
  el.classList.add('show')
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => {
    el.classList.remove('show')
  }, duration)
}
