<template>
  <div class="app-shell">
    <AppSidebar />

    <main ref="mainEl" class="main">
      <div v-if="scenarioLoading" class="top-progress"></div>

      <TopBar />
      <KpiGrid />

      <nav class="tabs" role="tablist">
        <button
          v-for="(t, i) in tabs"
          :key="t.id"
          class="tab"
          :class="{ active: activeTab === t.id }"
          :data-tab="t.id"
          :title="'快捷键 ' + (i + 1)"
          @click="switchTab(t.id)"
        >
          {{ t.label }}
        </button>
      </nav>

      <section v-if="loading" class="loading-wrap">
        <div v-for="n in 3" :key="n" class="skeleton-card">
          <div class="sk-line w40"></div>
          <div class="sk-line w80"></div>
          <div class="sk-line w60"></div>
        </div>
      </section>

      <template v-else>
        <OverviewPanel v-if="activeTab === 'overview'" />
        <QcPanel v-else-if="activeTab === 'qc'" />
        <LimitsPanel v-else-if="activeTab === 'limits'" />
        <RoutesPanel v-else-if="activeTab === 'routes'" />
        <CostPanel v-else-if="activeTab === 'cost'" />
        <PlanPanel v-else-if="activeTab === 'plan'" />
        <SourcesPanel v-else-if="activeTab === 'sources'" />
      </template>
    </main>

    <RightRail />

    <transition name="fade">
      <div v-if="calcOpen" class="drawer-scrim" @click="closeCalc"></div>
    </transition>
    <transition name="fade">
      <div v-if="chatOpen" class="drawer-scrim chat-scrim" @click="closeChat"></div>
    </transition>

    <CalcDrawer />
    <ChatDrawer />
    <SourceDrawer />
    <TestPlanDialog />
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

import AppSidebar from '@/components/AppSidebar.vue'
import TopBar from '@/components/TopBar.vue'
import KpiGrid from '@/components/KpiGrid.vue'
import OverviewPanel from '@/components/OverviewPanel.vue'
import QcPanel from '@/components/QcPanel.vue'
import LimitsPanel from '@/components/LimitsPanel.vue'
import RoutesPanel from '@/components/RoutesPanel.vue'
import CostPanel from '@/components/CostPanel.vue'
import PlanPanel from '@/components/PlanPanel.vue'
import SourcesPanel from '@/components/SourcesPanel.vue'
import RightRail from '@/components/RightRail.vue'
import CalcDrawer from '@/components/CalcDrawer.vue'
import ChatDrawer from '@/components/ChatDrawer.vue'
import SourceDrawer from '@/components/SourceDrawer.vue'
import TestPlanDialog from '@/components/TestPlanDialog.vue'

const store = useCaseStore()
const { tabs, activeTab, loading, scenarioLoading, calcOpen, chatOpen } = storeToRefs(store)
const { init, closeCalc, closeChat, switchTab } = store

const mainEl = ref(null)

watch(activeTab, id => {
  nextTick(() => {
    if (mainEl.value) mainEl.value.scrollTo({ top: 0, behavior: 'smooth' })
    const btn = document.querySelector(`.tab[data-tab="${id}"]`)
    if (btn && btn.scrollIntoView) btn.scrollIntoView({ inline: 'center', block: 'nearest', behavior: 'smooth' })
  })
})

const onKey = (e) => {
  if (e.target && e.target.closest && e.target.closest('input, textarea, select, .el-select')) return
  if (e.key === 'Escape') {
    closeCalc()
    closeChat()
    store.sourceOpen = false
    store.testPlanOpen = false
    return
  }
  const n = Number(e.key)
  if (n >= 1 && n <= tabs.value.length) switchTab(tabs.value[n - 1].id)
}

onMounted(() => {
  init()
  window.addEventListener('keydown', onKey)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
})
</script>
