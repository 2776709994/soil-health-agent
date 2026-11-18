<template>
  <aside class="right-rail">
    <section class="rail-card rail-current">
      <header>
        <span class="rail-title">当前地块</span>
        <span class="cell-tag" :class="selectedPlotData.status === 'limited' ? 'tag-orange' : selectedPlotData.status === 'watch' ? 'tag-amber' : 'tag-green'">{{ selectedPlotData.statusLabel }}</span>
      </header>
      <div class="current-id">{{ selectedPlotData.id }}</div>
      <div class="current-metrics">
        <div><span>pH</span><b>{{ selectedPlotData.ph.toFixed(1) }}</b></div>
        <div><span>ECe</span><b>{{ selectedPlotData.ece.toFixed(1) }}</b></div>
        <div><span>有机质</span><b>{{ selectedPlotData.om }}</b></div>
        <div><span>容重</span><b>{{ selectedPlotData.bd.toFixed(2) }}</b></div>
      </div>
      <button class="rail-link" @click="openCalc(selectedPlotData.id)">
        <app-icon name="calculator" :size="14" /> 查看计算明细
      </button>
    </section>

    <section class="rail-card rail-gap">
      <header>
        <span class="rail-title"><app-icon name="alert" :size="15" /> 数据缺口</span>
        <span class="count">5</span>
      </header>
      <ul>
        <li>ESP、SAR、CEC 未提供</li>
        <li>排水去向未提供</li>
        <li>主要离子未提供</li>
        <li>粪肥品质未检测</li>
      </ul>
      <p class="rail-note">钠化程度暂不可判定，石膏用量仅条件性建议。</p>
      <button class="rail-link" @click="openTestPlan">
        查看补测建议 <app-icon name="arrowRight" :size="13" />
      </button>
    </section>

    <section class="rail-card" :class="{ 'is-updating': scenarioLoading }">
      <header>
        <span class="rail-title">方案比较</span>
        <button class="link" @click="goRouteTab">查看全部</button>
      </header>
      <div v-for="r in routeList" :key="r.id" class="route-mini" @click="goRouteTab">
        <span class="route-mini-id">{{ r.id }}</span>
        <span class="route-mini-name">{{ r.name }}</span>
        <span class="cell-tag" :class="routeClass(r.displaySuitabilityKey)">{{ r.displaySuitability }}</span>
      </div>
    </section>

    <section class="rail-card">
      <header>
        <span class="rail-title">依据追溯</span>
        <button class="link" @click="goSourceTab">全部</button>
      </header>
      <div v-for="s in sources.slice(0, 3)" :key="s.id" class="source-mini" @click="openSource(s.id)">
        <app-icon name="fileText" :size="15" />
        <div>
          <div class="source-mini-title">{{ s.title }}</div>
          <div class="source-mini-meta">{{ s.meta }}</div>
        </div>
      </div>
    </section>
  </aside>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { selectedPlotData, routeList, sources, scenarioLoading } = storeToRefs(store)
const { openCalc, openTestPlan, goRouteTab, goSourceTab, openSource, routeClass } = store
</script>
