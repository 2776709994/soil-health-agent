<template>
  <section class="tab-panel">
    <div class="recommend-bar">
      <div class="recommend-icon"><app-icon name="target" :size="18" /></div>
      <div>
        <strong>推荐组合</strong>
        S01–S02 以 A 为主；S03 走 B + 定额淋洗；S04–S05 先排水、补测 ESP/SAR/CEC，C 仅条件性。
      </div>
    </div>

    <div v-if="isReduced" class="scenario-banner">
      <app-icon name="alert" :size="16" />
      供水上限 −25%：B/C 在 S03–S05 淋洗受限。建议转向 A + 覆盖/耐盐品种，并把 C 的排水改造放到第一年。
    </div>

    <section class="card">
      <header class="card-head">
        <div><h3>3 条改良路线比较</h3><p>先筛适用性，再比费用；不以低成本抵消安全目标</p></div>
      </header>
      <table class="data-table route-table">
        <thead>
          <tr>
            <th>路线</th><th>核心措施</th><th>适用地块</th><th>先决条件</th><th>两年费用（万元）</th><th>适用性</th><th>主要限制</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in routeList" :key="r.id">
            <td><span class="route-id">{{ r.id }}</span> {{ r.name }}</td>
            <td>{{ r.measures }}</td>
            <td>{{ r.plots }}</td>
            <td>{{ r.precondition }}</td>
            <td><span class="strong">{{ r.cost }}</span><br><span class="muted small">{{ r.costNote }}</span></td>
            <td><span class="cell-tag" :class="routeClass(r.displaySuitabilityKey)">{{ r.displaySuitability }}</span></td>
            <td class="muted">{{ r.limits }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <div class="note-band">
      <app-icon name="info" :size="16" />
      C 路线在 ESP/SAR/CEC 与排水去向缺失时不能给精确石膏用量；50–70 万元/两年可能超过 60 万元预算。
    </div>
  </section>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { routeList, isReduced } = storeToRefs(store)
const { routeClass } = store
</script>
