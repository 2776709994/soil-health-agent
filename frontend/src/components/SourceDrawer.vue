<template>
  <el-drawer v-model="sourceOpen" direction="rtl" size="380px" :with-header="false" class="source-drawer">
    <div class="drawer-head">
      <div>
        <span class="eyebrow">SOURCE</span>
        <h2>来源卡片</h2>
      </div>
      <button class="icon-btn" @click="sourceOpen = false" aria-label="关闭来源"><app-icon name="x" :size="17" /></button>
    </div>
    <div class="source-detail">
      <div class="source-tags">
        <span class="cell-tag" :class="sourceClass(currentSource.type)">{{ currentSource.type }}</span>
        <span class="cell-tag tag-amber">{{ currentSource.status }}</span>
      </div>
      <h3>{{ currentSource.title }}</h3>
      <p class="source-meta">{{ currentSource.meta }}</p>
      <div class="kv"><span>适用范围</span><p>{{ currentSource.scope }}</p></div>
      <div class="kv"><span>说明</span><p>{{ currentSource.note }}</p></div>
      <div class="source-warning">
        <app-icon name="alert" :size="15" />
        原型中的来源为占位；正式版必须替换为核对后的标准/论文条款。
      </div>
      <el-button class="btn-primary full" @click="copyCitation">
        <app-icon name="clipboard" :size="15" /> 复制引用
      </el-button>
    </div>
  </el-drawer>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'

const store = useCaseStore()
const { sourceOpen, currentSource } = storeToRefs(store)
const { sourceClass, copyCitation } = store
</script>
