<template>
  <aside class="calc-drawer" :class="{ open: calcOpen }" aria-label="计算明细">
    <header class="drawer-head">
      <div>
        <span class="eyebrow">CALCULATION</span>
        <h2>计算明细</h2>
      </div>
      <button class="icon-btn" @click="closeCalc" aria-label="关闭计算明细"><app-icon name="x" :size="17" /></button>
    </header>

    <div class="plot-pills">
      <button v-for="p in plots" :key="p.id" :class="{ active: p.id === selectedPlot }" @click="selectPlot(p.id)">{{ p.id }}</button>
    </div>

    <div class="drawer-scroll">
      <section class="calc-block">
        <h3>干土质量</h3>
        <div class="formula">M = A × d × ρ</div>
        <div class="calc-table">
          <div><span>A</span><b>{{ calc.area }} 亩 = {{ calc.areaM2Text }} m²</b></div>
          <div><span>d</span><b>0.2 m</b></div>
          <div><span>ρ</span><b>{{ calc.bdText }} t/m³</b></div>
        </div>
        <div class="calc-result"><span>M</span><strong>{{ calc.MText }} t</strong></div>
        <p class="calc-note">折合 {{ calc.perMuText }} t/亩（干基）。</p>
      </section>

      <section class="calc-block">
        <h3>淋洗需水（稳态估算）</h3>
        <div class="formula small">LR = ECw / (5 × ECe,t − ECw)</div>
        <div class="calc-table">
          <div><span>ECw</span><b>0.8 dS/m</b></div>
          <div><span>ECe,t</span><b>{{ calc.targetEce }} dS/m</b></div>
          <div><span>LR</span><b>{{ calc.lr }}</b></div>
          <div><span>根层</span><b>{{ calc.rootDepth }} m</b></div>
        </div>
        <div class="calc-result"><span>V</span><strong>{{ calc.waterTotalText }} m³/地块</strong></div>
        <p class="calc-note">约 {{ calc.waterPerMu }} m³/亩·年，低于 40 m³/(亩·年) 上限；初始盐分高时需多年。</p>
        <p v-if="calc.ece >= 5" class="calc-warn">
          该地块初始 ECe {{ calc.eceText }} dS/m，按质量平衡粗算需数百 m³/亩，两年内不能完全降到 2.5；以排水 + 分期为目标。
        </p>
      </section>

      <section class="calc-block">
        <h3>依据</h3>
        <button class="source-inline" @click="openSource('S-02')">
          <app-icon name="fileText" :size="15" />
          <span>S-02 · 土壤检测方法（待核对）</span>
          <app-icon name="chevronRight" :size="14" />
        </button>
        <p class="calc-note">计算为教学估算，不替代田间试验。所有阈值需组员按正式文本核对。</p>
      </section>
    </div>
  </aside>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { calc, calcOpen, plots, selectedPlot } = storeToRefs(store)
const { closeCalc, selectPlot, openSource } = store
</script>
