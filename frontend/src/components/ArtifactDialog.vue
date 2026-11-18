<template>
  <el-dialog v-model="artifactOpen" :title="artifactName || '产物预览'" width="760px" class="academic-dialog artifact-dialog">
    <pre class="artifact-content">{{ artifactContent }}</pre>
    <template #footer>
      <el-button @click="artifactOpen = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { artifactOpen, artifactName, artifactContent } = storeToRefs(store)
</script>
