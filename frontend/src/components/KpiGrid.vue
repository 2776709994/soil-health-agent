<template>
  <section class="kpi-grid">
    <article class="kpi-card">
      <div class="kpi-icon"><app-icon name="map" :size="19" /></div>
      <div class="kpi-body">
        <div class="kpi-value"><count-number :value="200" /><span>亩</span></div>
        <div class="kpi-label">总地块面积</div>
      </div>
    </article>
    <article class="kpi-card">
      <div class="kpi-icon"><app-icon name="dashboard" :size="19" /></div>
      <div class="kpi-body">
        <div class="kpi-value"><count-number :value="5" /><span>个地块</span></div>
        <div class="kpi-label">参与诊断地块</div>
      </div>
    </article>
    <article class="kpi-card">
      <div class="kpi-icon"><app-icon name="wallet" :size="19" /></div>
      <div class="kpi-body">
        <div class="kpi-value"><count-number :value="60" /><span>万元</span></div>
        <div class="kpi-label">两年改良预算</div>
      </div>
    </article>
    <article class="kpi-card" :class="{ warn: isReduced, 'is-updating': scenarioLoading }">
      <div class="kpi-icon"><app-icon name="droplet" :size="19" /></div>
      <div class="kpi-body">
        <div class="kpi-value"><count-number :value="kpiWater" /><span>m³/亩·年</span></div>
        <div class="kpi-label">{{ isReduced ? '供水上限 −25%' : '基础供水标准' }}</div>
      </div>
    </article>
  </section>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { isReduced, kpiWater, scenarioLoading } = storeToRefs(store)
</script>
