<template>
  <aside class="chat-drawer" :class="{ open: chatOpen }" aria-label="对话助手">
    <header class="drawer-head">
      <div>
        <span class="eyebrow">AGENT</span>
        <h2>对话助手</h2>
      </div>
      <button class="icon-btn" @click="closeChat" aria-label="关闭对话助手"><app-icon name="x" :size="17" /></button>
    </header>

    <div ref="chatBodyRef" class="chat-body">
      <div v-for="(m, i) in chatMessages" :key="i" class="chat-msg" :class="m.role">
        <div class="chat-avatar"><app-icon :name="m.role === 'user' ? 'chat' : 'leaf'" :size="15" /></div>
        <div class="chat-bubble" :class="{ error: m.error }">
          <div class="chat-text">{{ m.text }}</div>
          <details v-if="m.thinking" class="chat-thinking">
            <summary>思考过程</summary>
            <pre>{{ m.thinking }}</pre>
          </details>
        </div>
      </div>
      <div v-if="chatLoading" class="chat-msg assistant">
        <div class="chat-avatar"><app-icon name="leaf" :size="15" /></div>
        <div class="chat-bubble typing"><span></span><span></span><span></span></div>
      </div>
    </div>

    <div class="chat-input-wrap">
      <textarea
        v-model="chatInput"
        placeholder="问：S04 为什么只能条件性？三条路线怎么选？"
        @keydown.enter.exact.prevent="sendChat"
      ></textarea>
      <button class="chat-send" :disabled="chatLoading || !chatInput.trim()" @click="sendChat" aria-label="发送">
        <app-icon name="arrowRight" :size="16" />
      </button>
    </div>
    <div class="chat-foot">由 dsh + MiniMax-M3.1-Flash 驱动 · 回答仅为教学建议</div>
  </aside>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { chatOpen, chatMessages, chatLoading, chatInput } = storeToRefs(store)
const { closeChat, sendChat } = store

const chatBodyRef = ref(null)

const scrollBottom = () => {
  nextTick(() => {
    if (chatBodyRef.value) chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  })
}

watch(() => chatMessages.value.length, scrollBottom, { flush: 'post' })
watch(chatLoading, scrollBottom, { flush: 'post' })
</script>
