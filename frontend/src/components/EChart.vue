<template>
  <div ref="el" class="echart" :style="{ height }"></div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, MarkLineComponent } from 'echarts/components'
import { SVGRenderer } from 'echarts/renderers'

echarts.use([BarChart, GridComponent, TooltipComponent, MarkLineComponent, SVGRenderer])

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: String, default: '220px' },
})

const el = ref(null)
let chart = null
let ro = null

const render = () => {
  if (!el.value) return
  if (!chart) chart = echarts.init(el.value, null, { renderer: 'svg' })
  chart.setOption(props.option, { notMerge: false, lazyUpdate: true })
}

onMounted(() => {
  render()
  ro = new ResizeObserver(() => chart && chart.resize())
  ro.observe(el.value)
})

watch(() => props.option, render, { deep: true })

onUnmounted(() => {
  if (ro) ro.disconnect()
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>
