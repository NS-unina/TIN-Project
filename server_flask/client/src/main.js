import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.css'
import { reactive } from 'vue'

const app = createApp(App)

export const store = reactive({
    vmId: ""
  })

app.use(router)

app.mount('#app')