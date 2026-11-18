<template>
  <section class="agent-workspace">
    <header class="agent-head">
      <div>
        <div class="eyebrow">AGENT WORKBENCH</div>
        <h2>Agent 工作台</h2>
        <p>读取案例数据、调用工具、生成产物；ESP/SAR/CEC 缺失时会主动要求补测。</p>
      </div>
      <div class="agent-actions">
        <span class="agent-head-meta">{{ toolCount }} 工具 · 思考 low</span>
        <span class="agent-status" :class="statusClass">{{ agentStatus }}</span>
        <el-button class="btn-ghost" @click="switchTab('overview')">返回诊断</el-button>
        <el-button class="btn-ghost" @click="newAgentTask">新任务</el-button>
        <el-button v-if="agentRunning" class="btn-danger" @click="cancelAgent">停止</el-button>
      </div>
    </header>

    <div class="agent-main" :style="gridStyle">
      <aside class="agent-pane" :class="{ collapsed: historyCollapsed }">
        <template v-if="!historyCollapsed">
          <header class="pane-head">
            <span>历史会话</span>
            <div class="pane-actions">
              <button class="pane-link" @click="loadAgentSessions">刷新</button>
              <button class="pane-icon" title="收起历史" @click="historyCollapsed = true">‹</button>
            </div>
          </header>
          <div class="pane-scroll">
            <div v-if="!agentSessions.length" class="agent-empty-side">还没有历史会话。</div>
            <div
              v-for="s in agentSessions"
              :key="s.id"
              class="session-row"
              :class="{ active: s.id === agentCurrentKey }"
              @click="selectAgentSession(s.id)"
            >
              <div class="session-main">
                <div class="session-title">{{ s.title }}</div>
                <div class="session-meta">{{ formatTime(s.updatedAt) }} · {{ s.status || '—' }}</div>
              </div>
              <button class="session-del" title="删除会话" @click.stop="deleteAgentSession(s.id)">×</button>
            </div>
          </div>
        </template>
        <button v-else class="pane-rail" title="展开历史" @click="historyCollapsed = false">
          <app-icon name="history" :size="16" />
          <span>历史</span>
        </button>
      </aside>

      <div class="agent-chat-pane">
        <section ref="threadRef" class="agent-thread card">
          <div class="agent-thread-scroll">
            <div v-if="!agentMessages.length && !agentFinal" class="agent-empty">
              <div class="agent-empty-icon"><app-icon name="flask" :size="26" /></div>
              <h3>让 Agent 帮你干活</h3>
              <p>不只是问答：它会读文件、调用工具、执行计算，并把结果写成文件。</p>
              <div class="agent-suggestions">
                <button
                  v-for="s in suggestions"
                  :key="s"
                  class="agent-suggestion"
                  @click="runSuggestion(s)"
                >
                  {{ s }}
                </button>
              </div>
            </div>

            <div v-for="(m, i) in agentMessages" :key="i" class="agent-item">
              <div v-if="m.kind === 'user'" class="agent-user">
                <span class="agent-role">你</span>
                <div class="agent-user-text">{{ m.text }}</div>
              </div>

              <details v-else-if="m.kind === 'thinking'" class="agent-thinking">
                <summary><app-icon name="activity" :size="13" /> 思考过程</summary>
                <pre>{{ m.text }}</pre>
              </details>

              <div v-else-if="m.kind === 'text'" class="agent-text">
                <app-icon name="chat" :size="14" />
                <MarkdownView :text="m.text" />
              </div>

              <div v-else-if="m.kind === 'tool'" class="agent-tool">
                <header>
                  <span class="tool-name"><app-icon name="layers" :size="14" /> {{ m.tool }}</span>
                  <span class="cell-tag" :class="m.status === 'completed' ? 'tag-green' : m.status === 'error' ? 'tag-red' : 'tag-amber'">
                    {{ m.status === 'completed' ? '完成' : m.status === 'error' ? '失败' : '执行中' }}
                  </span>
                </header>
                <details>
                  <summary>输入 / 结果</summary>
                  <pre class="tool-input">{{ JSON.stringify(m.input, null, 2) }}</pre>
                  <pre v-if="m.result" class="tool-result">{{ m.result }}</pre>
                </details>
              </div>
            </div>

            <div v-if="agentRunning" class="agent-running">
              <span class="typing"><span></span><span></span><span></span></span>
              Agent 正在执行…
            </div>

            <div v-if="agentError" class="agent-error">
              <app-icon name="alert" :size="15" />
              {{ agentError }}
            </div>

            <div v-if="agentFinal" class="agent-final">
              <header><app-icon name="check" :size="15" /> 最终答案</header>
              <MarkdownView :text="agentFinal" />
            </div>
          </div>
        </section>

        <div class="agent-composer card">
          <textarea
            v-model="agentPrompt"
            placeholder="例如：诊断 5 个地块，比较 3 条路线，并写出 outputs/plan.md"
            @keydown.enter.exact.prevent="submit"
          ></textarea>
          <button class="chat-send" :disabled="agentRunning || !agentPrompt.trim()" @click="submit" aria-label="发送任务">
            <app-icon name="arrowRight" :size="16" />
          </button>
        </div>
      </div>

      <aside class="agent-pane" :class="{ collapsed: artifactsCollapsed }">
        <template v-if="!artifactsCollapsed">
          <header class="pane-head">
            <span>产出文件</span>
            <div class="pane-actions">
              <button class="pane-link" @click="refreshArtifacts">刷新</button>
              <button class="pane-icon" title="收起产物" @click="artifactsCollapsed = true">›</button>
            </div>
          </header>
          <div class="pane-scroll">
            <div v-if="!agentArtifacts.length" class="agent-empty-side">还没有文件。让 Agent 写 <code>outputs/...</code>。</div>
            <div v-for="f in agentArtifacts" :key="f.path" class="artifact-row" @click="openArtifact(f.path)">
              <app-icon name="fileText" :size="14" />
              <span class="artifact-name">{{ f.name }}</span>
              <span class="muted small">{{ (f.size / 1024).toFixed(1) }} KB</span>
            </div>
          </div>
        </template>
        <button v-else class="pane-rail" title="展开产物" @click="artifactsCollapsed = false">
          <app-icon name="fileText" :size="16" />
          <span>产物</span>
        </button>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useCaseStore } from '@/stores/useCaseStore'
import MarkdownView from '@/components/MarkdownView.vue'

const store = useCaseStore()
const {
  agentMessages,
  agentPrompt,
  agentRunning,
  agentStatus,
  agentError,
  agentFinal,
  agentTaskId,
  agentSessionId,
  agentArtifacts,
  agentSessions,
  agentCurrentKey,
} = storeToRefs(store)
const {
  runAgent,
  cancelAgent,
  newAgentTask,
  refreshArtifacts,
  openArtifact,
  switchTab,
  selectAgentSession,
  deleteAgentSession,
  loadAgentSessions,
} = store

const suggestions = [
  '诊断 5 个地块，说明每个地块的主要限制，并给出分地块建议。',
  '比较 A/B/C 三条路线，核算两年费用、材料与淋洗水，写成 outputs/route-compare.md。',
  '只生成两年实施与监测计划，写入 outputs/two-year-plan.md，最终回答 200 字摘要，不要重复诊断。',
]

const historyCollapsed = ref(false)
const artifactsCollapsed = ref(false)
const threadRef = ref(null)

const gridStyle = computed(() => ({
  gridTemplateColumns: `${historyCollapsed.value ? '46px' : '240px'} minmax(0, 1fr) ${artifactsCollapsed.value ? '46px' : '260px'}`,
}))

const toolCount = computed(() => agentMessages.value.filter(m => m.kind === 'tool').length)
const statusClass = computed(() => {
  if (agentStatus.value === '完成') return 'tag-green'
  if (agentStatus.value === '失败') return 'tag-red'
  if (agentStatus.value === '运行中' || agentStatus.value === '执行中') return 'tag-amber'
  return 'tag-gray'
})

const formatTime = ts => {
  if (!ts) return '—'
  return new Date(ts).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const scrollThread = () => {
  nextTick(() => {
    if (threadRef.value) threadRef.value.scrollTop = threadRef.value.scrollHeight
  })
}

watch(() => agentMessages.value.length, scrollThread, { flush: 'post' })
watch(agentRunning, scrollThread, { flush: 'post' })
watch(agentFinal, scrollThread, { flush: 'post' })

const submit = () => runAgent(agentPrompt.value)
const runSuggestion = text => runAgent(text)
</script>
