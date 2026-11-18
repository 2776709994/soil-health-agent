<template>
  <section class="tab-panel">
    <div class="limit-grid">
      <article
        v-for="p in plots"
        :key="p.id"
        class="limit-card"
        :class="{ selected: p.id === selectedPlot }"
        @click="selectPlot(p.id)"
      >
        <header>
          <div class="limit-id">{{ p.id }}</div>
          <span class="cell-tag" :class="p.status === 'limited' ? 'tag-orange' : p.status === 'watch' ? 'tag-amber' : 'tag-green'">{{ p.statusLabel }}</span>
        </header>
        <div class="limit-tags">
          <span v-for="t in p.limits" :key="t" class="cell-tag" :class="limitClass(t)">{{ t }}</span>
        </div>
        <p class="limit-note">{{ p.note }}</p>
        <div class="limit-rules">规则：{{ p.rules.join(' · ') }}</div>
        <div class="limit-foot">
          <span>ECe {{ p.ece.toFixed(1) }}</span>
          <span>pH {{ p.ph.toFixed(1) }}</span>
          <span>出苗 {{ p.emergence }}%</span>
        </div>
      </article>
    </div>
    <div class="note-band">
      <app-icon name="info" :size="16" />
      钠化：5 个地块均待测（ESP/SAR/CEC 缺失），不能仅凭 pH 或 ECe 判定。排水分级为教师给定，去向与水质仍需调查。
    </div>
  </section>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { plots, selectedPlot } = storeToRefs(store)
const { selectPlot, limitClass } = store
</script>
