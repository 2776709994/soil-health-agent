<template>
  <section class="tab-panel">
    <div class="source-stats">
      <span class="provenance-chip teacher">标准/官方 · 3</span>
      <span class="provenance-chip retrieved">论文 · 2 / 目标 8</span>
      <span class="provenance-chip simulated">学生模拟 · 0 / 目标 6</span>
      <span class="source-stat-note">原型仅展示 5 条示例；正式版补足 ≥20 份并逐条核对</span>
    </div>

    <div class="filter-row">
      <button
        v-for="f in ['全部', '标准', '论文', '官方']"
        :key="f"
        class="chip"
        :class="{ active: sourceFilter === f }"
        @click="sourceFilter = f"
      >
        {{ f }}
      </button>
    </div>

    <div class="source-grid">
      <article v-for="s in filteredSources" :key="s.id" class="source-card" @click="openSource(s.id)">
        <header>
          <span class="cell-tag" :class="sourceClass(s.type)">{{ s.type }}</span>
          <span class="cell-tag tag-amber">{{ s.status }}</span>
        </header>
        <h3>{{ s.title }}</h3>
        <p class="source-meta">{{ s.meta }}</p>
        <p class="source-scope">{{ s.scope }}</p>
        <span class="link">查看来源卡片 <app-icon name="arrowRight" :size="13" /></span>
      </article>
    </div>

    <div class="note-band">
      <app-icon name="alert" :size="16" />
      当前为原型占位：标准号、条款号、论文信息必须由组员在正式文本中核对后替换，不能直接使用 AI 生成值。
    </div>
  </section>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { sourceFilter, filteredSources } = storeToRefs(store)
const { sourceClass, openSource } = store
</script>
