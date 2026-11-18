<template>
  <section class="tab-panel">
    <div class="timeline">
      <article v-for="p in plan" :key="p.period" class="timeline-card">
        <div class="timeline-period">{{ p.period }}</div>
        <h3>{{ p.title }}</h3>
        <ul>
          <li v-for="t in p.tasks" :key="t">{{ t }}</li>
        </ul>
      </article>
    </div>

    <section class="card">
      <header class="card-head">
        <div><h3>两年监测计划</h3><p>土壤—排水—作物配套</p></div>
      </header>
      <table class="data-table">
        <thead><tr><th>指标</th><th>频率</th><th>点位</th><th>目的</th></tr></thead>
        <tbody>
          <tr v-for="m in monitoring" :key="m.indicator">
            <td class="strong">{{ m.indicator }}</td>
            <td>{{ m.frequency }}</td>
            <td>{{ m.points }}</td>
            <td class="muted">{{ m.purpose }}</td>
          </tr>
        </tbody>
      </table>
      <p class="note-text">出苗率只用于描述现状，不作为措施效果；效果验证需结合对照与重复监测。</p>
    </section>
  </section>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { plan, monitoring } = storeToRefs(store)
</script>
