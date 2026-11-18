<template>
  <header class="topbar">
    <div class="title-block">
      <div class="eyebrow">土壤健康诊断 · 精准改良</div>
      <h1>{{ meta.caseTitle }}</h1>
      <p>{{ meta.subtitle }}</p>
    </div>
    <div class="top-actions">
      <el-select
        :model-value="scenario"
        class="scenario-select"
        popper-class="academic-popper"
        @change="changeScenario"
      >
        <el-option
          v-for="o in scenarioOptions"
          :key="o.value"
          :label="o.label"
          :value="o.value"
        ></el-option>
      </el-select>
      <el-tag class="budget-tag" effect="plain">
        <app-icon name="wallet" :size="14" /> 预算 60 万元
      </el-tag>
      <el-button class="btn-ghost" :loading="reanalyzing" @click="reanalyze">
        <app-icon name="refresh" :size="15" /> 重新分析
      </el-button>
      <el-button class="btn-primary" :loading="exporting" @click="exportReport">
        <app-icon name="download" :size="15" /> 导出报告
      </el-button>
    </div>
  </header>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { meta, scenario, scenarioOptions, reanalyzing, exporting } = storeToRefs(store)
const { changeScenario, reanalyze, exportReport } = store
</script>
