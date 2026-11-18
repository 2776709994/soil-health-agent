import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import '@/styles/global.css'

import App from './App.vue'
import AppIcon from '@/components/AppIcon.vue'
import EChart from '@/components/EChart.vue'
import CountNumber from '@/components/CountNumber.vue'

const app = createApp(App)
app.use(createPinia())
app.use(ElementPlus)
app.component('app-icon', AppIcon)
app.component('e-chart', EChart)
app.component('count-number', CountNumber)
app.mount('#app')
