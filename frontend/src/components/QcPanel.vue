<template>
  <section class="tab-panel">
    <div class="mini-kpi-grid">
      <article class="mini-kpi"><strong>5</strong><span>地块记录</span></article>
      <article class="mini-kpi"><strong>5 / 10</strong><span>关键字段完整</span></article>
      <article class="mini-kpi warn"><strong>5</strong><span>缺失/待补测项</span></article>
      <article class="mini-kpi"><strong>5 / 5</strong><span>数值范围检查通过</span></article>
    </div>

    <section class="card">
      <header class="card-head">
        <div><h3>质控与缺失检查</h3><p>单位、缺失、负值、方法口径</p></div>
      </header>
      <table class="data-table">
        <thead><tr><th>检查项</th><th>结果</th><th>说明</th><th>处理</th></tr></thead>
        <tbody>
          <tr v-for="q in qc" :key="q.item">
            <td class="strong">{{ q.item }}</td>
            <td><span class="cell-tag" :class="q.level === 'ok' ? 'tag-green' : q.level === 'warn' ? 'tag-amber' : 'tag-blue'">{{ q.result }}</span></td>
            <td>{{ q.detail }}</td>
            <td class="muted">{{ q.action }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="card">
      <header class="card-head">
        <div><h3>数据来源分层</h3><p>教师数据不覆盖、模拟数据单独标注</p></div>
      </header>
      <div class="provenance-row">
        <span class="provenance-chip teacher">教师给定 · 5</span>
        <span class="provenance-chip retrieved">检索资料 · 8</span>
        <span class="provenance-chip simulated">学生模拟 · 7</span>
      </div>
      <p class="note-text">正式版在数据表上直接显示来源徽章；参数表记录单位、干湿基、适用范围与出处。所有标准阈值需组员逐条核对。</p>
    </section>
  </section>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { qc } = storeToRefs(store)
</script>
