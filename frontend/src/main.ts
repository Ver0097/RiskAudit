import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// 应用入口：Task 17 会加入 router
const app = createApp(App)
app.use(createPinia())
app.mount('#app')
