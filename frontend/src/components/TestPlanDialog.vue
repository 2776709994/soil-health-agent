<template>
  <el-dialog v-model="testPlanOpen" title="补测建议（示意）" width="640px" class="academic-dialog">
    <table class="data-table compact">
      <thead><tr><th>项目</th><th>目的</th><th>方法/依据</th><th>优先级</th></tr></thead>
      <tbody>
        <tr v-for="t in testPlan" :key="t.item">
          <td class="strong">{{ t.item }}</td>
          <td>{{ t.purpose }}</td>
          <td class="muted">{{ t.method }}</td>
          <td><span class="cell-tag" :class="t.priority === '高' ? 'tag-red' : t.priority === '中' ? 'tag-amber' : 'tag-gray'">{{ t.priority }}</span></td>
        </tr>
      </tbody>
    </table>
    <p class="dialog-note">费用待询价；本表为教学建议，不替代法定检测。</p>
    <template #footer>
      <el-button @click="testPlanOpen = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { testPlanOpen, testPlan } = storeToRefs(store)
</script>
