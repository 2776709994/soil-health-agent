<template>
  <span class="count-number">{{ text }}</span>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  value: { type: Number, required: true },
  duration: { type: Number, default: 520 },
  decimals: { type: Number, default: 0 },
})

const display = ref(0)
let raf = 0
const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches

const animate = (from, to) => {
  if (reduced) {
    display.value = to
    return
  }
  cancelAnimationFrame(raf)
  const start = performance.now()
  const delta = to - from
  const tick = now => {
    const t = Math.min(1, (now - start) / props.duration)
    const eased = 1 - Math.pow(1 - t, 3)
    display.value = from + delta * eased
    if (t < 1) raf = requestAnimationFrame(tick)
  }
  raf = requestAnimationFrame(tick)
}

onMounted(() => animate(0, props.value))
watch(() => props.value, (to, from) => animate(from == null ? 0 : from, to))
onUnmounted(() => cancelAnimationFrame(raf))

const text = computed(() => {
  const v = props.decimals ? display.value.toFixed(props.decimals) : Math.round(display.value)
  return Number(v).toLocaleString('zh-CN')
})
</script>
