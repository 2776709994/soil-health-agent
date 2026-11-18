<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark"><app-icon name="layers" :size="24" /></div>
      <div class="brand-text">
        <strong>盐碱地精准改良</strong>
        <span>土壤健康诊断与精准改良 Agent</span>
      </div>
    </div>

    <nav class="nav">
      <div v-for="group in navGroups" :key="group.label" class="nav-group">
        <div class="nav-group-label">{{ group.label }}</div>
        <button
          v-for="item in group.items"
          :key="item.id"
          class="nav-item"
          :class="{ active: item.active || (item.id === 'chat' && chatOpen) }"
          @click="handleNav(item)"
        >
          <app-icon :name="item.icon" :size="17" />
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.count" class="nav-count">{{ item.count }}</span>
        </button>
      </div>
    </nav>

    <div class="plot-section">
      <div class="plot-section-head">
        <span>地块</span>
        <span class="muted">5</span>
      </div>
      <button
        v-for="p in plots"
        :key="p.id"
        class="plot-item"
        :class="{ selected: p.id === selectedPlot }"
        @click="selectPlot(p.id)"
      >
        <span class="plot-dot" :class="'dot-' + p.status"></span>
        <span class="plot-main">
          <span class="plot-id">{{ p.id }}</span>
          <span class="plot-meta">{{ p.area }} 亩 · ECe {{ p.ece.toFixed(1) }} dS/m</span>
          <span class="plot-sub">
            <span>{{ p.statusLabel }}</span>
            <span v-if="p.drainageKey === 'poor'" class="mini-badge">排水受限</span>
          </span>
        </span>
      </button>
      <button class="link-btn" @click="switchTab('limits')">
        查看全部地块 <app-icon name="arrowRight" :size="13" />
      </button>
    </div>

    <div class="sidebar-foot">
      <span class="foot-dot"></span> 教学模拟数据 · 不替代实测
    </div>
  </aside>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { navGroups, plots, selectedPlot, chatOpen } = storeToRefs(store)
const { handleNav, selectPlot, switchTab } = store
</script>
