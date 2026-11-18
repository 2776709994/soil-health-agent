<template>
  <section class="tab-panel">
    <div class="split-grid">
      <section class="card">
        <header class="card-head">
          <div><h3>资源供需</h3><p>秸秆、粪肥、额外淋洗水</p></div>
        </header>
        <div class="resource-list">
          <div v-for="r in resourceRows" :key="r.name" class="resource-row">
            <div class="resource-head">
              <span>{{ r.name }}</span>
              <span class="mono">需 {{ r.demand }} / 供 {{ r.supply }} {{ r.unit }}</span>
            </div>
            <div class="bar"><span :style="{ width: Math.min(100, r.pct) + '%' }" :class="{ over: r.over }"></span></div>
            <div class="resource-note">
              {{ r.note }}
              <span v-if="r.over" class="cell-tag tag-red">缺口</span>
            </div>
          </div>
        </div>
        <p class="note-text">秸秆按 30% 产炭率、粪肥按 7.5 t/ha 估算；均为示意，需按组员查证参数替换。</p>
      </section>

      <section class="card">
        <header class="card-head">
          <div><h3>费用构成</h3><p>两年合计，含运输、施用、监测与管理</p></div>
        </header>
        <table class="data-table compact">
          <thead><tr><th>项目</th><th>金额</th><th>占比</th></tr></thead>
          <tbody>
            <tr v-for="c in costRows" :key="c.item">
              <td>{{ c.item }}<br><span class="muted small">{{ c.note }}</span></td>
              <td class="mono">{{ c.amount.toFixed(1) }} 万元</td>
              <td><div class="bar small"><span :style="{ width: c.pct + '%' }"></span></div></td>
            </tr>
          </tbody>
        </table>
        <div class="budget-card">
          <div class="budget-line"><span>两年总费用</span><strong>{{ costTotal.toFixed(1) }} 万元</strong></div>
          <div class="budget-line"><span>预算</span><strong>60.0 万元</strong></div>
          <div class="bar"><span :style="{ width: budgetPct + '%' }"></span></div>
          <p>剩余 {{ budgetLeft }} 万元。价格为示意，需替换为组员查证单价。</p>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { resourceRows, costRows, costTotal, budgetPct, budgetLeft } = storeToRefs(store)
</script>
