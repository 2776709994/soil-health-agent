<template>
  <section class="tab-panel">
    <div class="insight-bar">
      <div class="insight-icon"><app-icon name="alert" :size="18" /></div>
      <div class="insight-text">
        <strong>诊断提示</strong>
        S04/S05 排水受限；ESP/SAR/CEC 缺失，钠化暂不可判定。建议先补测，再决定是否采用 C 路线。
      </div>
      <button class="link-btn" @click="openTestPlan">
        查看补测建议 <app-icon name="arrowRight" :size="13" />
      </button>
    </div>

    <section class="card table-card">
      <header class="card-head">
        <div>
          <h3>分地块诊断</h3>
          <p>点击地块或数值查看计算明细</p>
        </div>
        <div class="legend">
          <span class="legend-item"><i class="legend-dot light"></i>轻度</span>
          <span class="legend-item"><i class="legend-dot moderate"></i>中度</span>
          <span class="legend-item"><i class="legend-dot poor"></i>排水受限</span>
          <span class="legend-item"><i class="legend-dot gray"></i>待测</span>
        </div>
      </header>

      <div class="table-wrap">
        <table class="diag-table">
          <thead>
            <tr>
              <th class="row-head">指标</th>
              <th
                v-for="p in plots"
                :key="p.id"
                :class="{ selected: p.id === selectedPlot, 'warn-col': p.drainageKey === 'poor' }"
              >
                <button class="plot-head" @click="selectPlot(p.id)">
                  <span>{{ p.id }}</span>
                  <app-icon v-if="p.drainageKey === 'poor'" name="alert" :size="12" class="warn-icon" />
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in tableRows" :key="row.key">
              <th class="row-head">
                <span>{{ row.label }}</span>
                <span v-if="row.unit" class="unit">{{ row.unit }}</span>
              </th>
              <td
                v-for="p in plots"
                :key="p.id"
                :class="{
                  selected: p.id === selectedPlot,
                  'warn-col': p.drainageKey === 'poor',
                  'num-cell': row.clickable,
                }"
                @click="row.clickable && openCalc(p.id)"
              >
                <template v-if="row.kind === 'ece'">
                  <span class="ece-cell" :class="'salt-' + p.saltKey">
                    <b>{{ p.ece.toFixed(1) }}</b>
                    <span class="mini-tag">{{ p.saltClass }}</span>
                  </span>
                </template>
                <template v-else-if="row.kind === 'tag'">
                  <span v-for="(t, ti) in row.tags(p)" :key="ti" class="cell-tag" :class="t.cls">{{ t.text }}</span>
                </template>
                <template v-else>
                  <span class="num-value">{{ row.value(p) }}</span>
                  <span v-if="row.clickable" class="fn">ƒ</span>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <footer class="table-foot">
        <span>ECe 为 25℃饱和糊状土浸提液电导率；pH 为土:水=1:2.5。</span>
        <span>钠化：5 个地块均待测（ESP/SAR/CEC 缺失）。</span>
      </footer>
    </section>

    <div class="chart-row">
      <section class="card chart-card">
        <header class="card-head compact">
          <div>
            <h3>ECe 盐分分档</h3>
            <p>25℃饱和糊状土浸提液</p>
          </div>
          <span class="unit-chip">dS/m</span>
        </header>
        <e-chart :option="eceOption" height="214px" />
        <div class="chart-legend">
          <span class="legend-item"><i class="legend-dot light"></i>轻度</span>
          <span class="legend-item"><i class="legend-dot moderate"></i>中度</span>
          <span class="legend-line"></span>
          <span>阈值 2 / 4 / 8</span>
        </div>
      </section>

      <section class="card chart-card">
        <header class="card-head compact">
          <div>
            <h3>玉米相对产量潜力</h3>
            <p>仅按盐分胁迫估算</p>
          </div>
          <span class="unit-chip">%</span>
        </header>
        <e-chart :option="yieldOption" height="214px" />
        <div class="chart-legend">
          <span>用于诊断，不是产量预测</span>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { plots, selectedPlot, tableRows, eceOption, yieldOption } = storeToRefs(store)
const { selectPlot, openCalc, openTestPlan } = store
</script>
