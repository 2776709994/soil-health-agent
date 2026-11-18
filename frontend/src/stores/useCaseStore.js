import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'
import CASE_DATA from '@/data/case'

const DATA = CASE_DATA
const API_BASE = import.meta.env.VITE_API_BASE || ''

export const useCaseStore = defineStore('case', () => {
  const loading = ref(true)
  const scenarioLoading = ref(false)
  const reanalyzing = ref(false)
  const exporting = ref(false)
  const activeTab = ref('overview')
  const selectedPlot = ref('S04')
  const scenario = ref('base')
  const calcOpen = ref(false)
  const sourceOpen = ref(false)
  const activeSourceId = ref('S-02')
  const testPlanOpen = ref(false)
  const sourceFilter = ref('全部')
  const chatOpen = ref(false)
  const chatLoading = ref(false)
  const chatInput = ref('')
  const chatMessages = ref([
    {
      role: 'assistant',
      text: '我是土壤健康诊断助手。可以问我：S04 为什么只能条件性？三条路线怎么选？两年预算怎么分？',
      thinking: '',
    },
  ])

  const tabs = ref([
    { id: 'overview', label: '总览' },
    { id: 'qc', label: '数据与质控' },
    { id: 'limits', label: '限制因素' },
    { id: 'routes', label: '方案比较' },
    { id: 'cost', label: '资源与费用' },
    { id: 'plan', label: '两年计划' },
    { id: 'sources', label: '依据追溯' },
  ])

  const navGroups = ref([
    {
      label: '工作台',
      items: [
        { id: 'console', label: '诊断工作台', icon: 'dashboard', active: true },
        { id: 'chat', label: '对话助手', icon: 'chat' },
      ],
    },
    {
      label: '记录与知识',
      items: [
        { id: 'records', label: '诊断记录', icon: 'history', count: 3 },
        { id: 'library', label: '资料库', icon: 'book', count: 20 },
      ],
    },
    {
      label: '系统',
      items: [{ id: 'settings', label: '设置', icon: 'settings' }],
    },
  ])

  const scenarioOptions = ref([
    { value: 'base', label: '基础供水 40 m³/(亩·年)' },
    { value: 'reduced', label: '供水上限 −25% · 30 m³/(亩·年)' },
  ])

  const plots = ref(DATA.plots)
  const selectedPlotData = computed(() => plots.value.find(p => p.id === selectedPlot.value) || plots.value[0])
  const isReduced = computed(() => scenario.value === 'reduced')
  const kpiWater = computed(() => (isReduced.value ? 30 : 40))

  const routeList = computed(() => DATA.routes.map(r => {
    const reducedTag = isReduced.value && r.id !== 'A' ? '淋洗受限' : ''
    return {
      ...r,
      scenarioTag: reducedTag,
      displaySuitability: reducedTag || r.suitability,
      displaySuitabilityKey: reducedTag ? 'conditional' : r.suitabilityKey,
    }
  }))

  const limitClass = (t) => {
    if (t.includes('盐')) return 'tag-amber'
    if (t.includes('排水')) return 'tag-orange'
    if (t.includes('压实')) return 'tag-gray'
    if (t.includes('有机质')) return 'tag-blue'
    return 'tag-gray'
  }

  const tableRows = ref([
    { key: 'ph', label: 'pH', unit: '(1:2.5)', clickable: true, value: p => p.ph.toFixed(1) },
    { key: 'ece', label: 'ECe', unit: '(dS/m)', clickable: true, kind: 'ece' },
    { key: 'om', label: '有机质', unit: '(g/kg)', clickable: true, value: p => p.om },
    { key: 'bd', label: '容重', unit: '(g/cm³)', clickable: true, value: p => p.bd.toFixed(2) },
    {
      key: 'drainage',
      label: '排水',
      kind: 'tag',
      tags: p => [{
        text: p.drainage,
        cls: p.drainageKey === 'good' ? 'tag-green' : p.drainageKey === 'fair' ? 'tag-amber' : 'tag-orange',
      }],
    },
    { key: 'emergence', label: '出苗率', unit: '(%)', clickable: true, value: p => p.emergence },
    {
      key: 'salt',
      label: '盐分等级',
      kind: 'tag',
      tags: p => [{ text: p.saltClass, cls: p.saltKey === 'light' ? 'tag-green' : 'tag-amber' }],
    },
    { key: 'sodicity', label: '钠化', kind: 'tag', tags: () => [{ text: '待测', cls: 'tag-gray' }] },
    {
      key: 'limits',
      label: '主要限制',
      kind: 'tag',
      tags: p => p.limits.map(t => ({ text: t, cls: limitClass(t) })),
    },
    {
      key: 'rec',
      label: '建议',
      kind: 'tag',
      tags: p => [{ text: p.rec, cls: p.rec === '先排水' || p.rec === '分阶段' ? 'tag-orange' : 'tag-green' }],
    },
  ])

  const eceOption = computed(() => {
    const selected = selectedPlot.value
    const colorOf = p => (p.saltKey === 'light' ? '#7C9A72' : p.saltKey === 'moderate' ? '#C49A4A' : '#A65A3A')
    return {
      animationDuration: 420,
      animationDurationUpdate: 320,
      animationEasingUpdate: 'cubicOut',
      grid: { left: 46, right: 42, top: 20, bottom: 26 },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: '#2B2A26',
        borderWidth: 0,
        textStyle: { color: '#FFFDF8', fontSize: 12 },
        transitionDuration: 0.15,
        extraCssText: 'box-shadow:0 8px 24px rgba(40,35,25,.18);border-radius:4px;',
        formatter: params => {
          const p = params[0]
          return `${p.name}<br/>ECe ${Number(p.value).toFixed(1)} dS/m`
        },
      },
      xAxis: {
        type: 'value',
        min: 0,
        max: 10,
        interval: 2,
        axisLabel: { color: '#8A8272', fontSize: 10 },
        splitLine: { lineStyle: { color: '#EEE7DA' } },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'category',
        inverse: true,
        data: plots.value.map(p => p.id),
        axisTick: { show: false },
        axisLine: { show: false },
        axisLabel: { color: '#5C574C', fontSize: 11 },
      },
      series: [{
        type: 'bar',
        barWidth: 11,
        data: plots.value.map(p => ({
          value: p.ece,
          itemStyle: {
            color: colorOf(p),
            borderRadius: [0, 3, 3, 0],
            borderColor: p.id === selected ? '#2F4A2C' : 'transparent',
            borderWidth: p.id === selected ? 1.5 : 0,
          },
        })),
        label: {
          show: true,
          position: 'right',
          formatter: params => Number(params.value).toFixed(1),
          color: '#5C574C',
          fontSize: 11,
        },
        emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(79,107,74,.22)' } },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#B9AE99', type: 'dashed', width: 1 },
          label: { show: false },
          data: [{ xAxis: 2 }, { xAxis: 4 }, { xAxis: 8 }],
        },
      }],
    }
  })

  const yieldOption = computed(() => {
    const selected = selectedPlot.value
    return {
      animationDuration: 420,
      animationDurationUpdate: 320,
      animationEasingUpdate: 'cubicOut',
      grid: { left: 44, right: 20, top: 30, bottom: 26 },
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#2B2A26',
        borderWidth: 0,
        textStyle: { color: '#FFFDF8', fontSize: 12 },
        transitionDuration: 0.15,
        extraCssText: 'box-shadow:0 8px 24px rgba(40,35,25,.18);border-radius:4px;',
        formatter: params => `${params[0].name}<br/>相对产量潜力 ${params[0].value}%`,
      },
      xAxis: {
        type: 'category',
        data: plots.value.map(p => p.id),
        axisTick: { show: false },
        axisLine: { lineStyle: { color: '#DDD4C4' } },
        axisLabel: { color: '#5C574C', fontSize: 11 },
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        interval: 20,
        axisLabel: { formatter: '{value}%', color: '#8A8272', fontSize: 10 },
        splitLine: { lineStyle: { color: '#EEE7DA' } },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [{
        type: 'bar',
        barWidth: 20,
        data: plots.value.map(p => ({
          value: p.yieldPotential,
          itemStyle: { color: p.id === selected ? '#3F5A3A' : '#7C9A72', borderRadius: [3, 3, 0, 0] },
        })),
        label: { show: true, position: 'top', formatter: '{c}%', color: '#5C574C', fontSize: 11 },
        emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(79,107,74,.22)' } },
      }],
    }
  })

  const resourceRows = computed(() => DATA.resources.map(r => {
    const supply = r.name.includes('淋洗') && isReduced.value ? 30 : r.supply
    const demand = r.demand
    return { ...r, supply, demand, pct: Math.round(demand / supply * 100), over: demand > supply }
  }))

  const costRows = computed(() => DATA.cost.map(c => ({
    ...c,
    pct: Math.round(c.amount / DATA.totals.cost * 100),
  })))
  const costTotal = computed(() => DATA.totals.cost)
  const budgetPct = computed(() => Math.min(100, Math.round(costTotal.value / DATA.meta.budgetWan * 100)))
  const budgetLeft = computed(() => (DATA.meta.budgetWan - costTotal.value).toFixed(1))

  const currentSource = computed(() => DATA.sources.find(s => s.id === activeSourceId.value) || DATA.sources[0])
  const filteredSources = computed(() => {
    if (sourceFilter.value === '全部') return DATA.sources
    if (sourceFilter.value === '官方') return DATA.sources.filter(s => s.type.includes('官方'))
    return DATA.sources.filter(s => s.type === sourceFilter.value)
  })

  const calc = computed(() => {
    const p = selectedPlotData.value
    return {
      ...p,
      MText: p.M.toLocaleString('zh-CN'),
      perMuText: p.perMu.toLocaleString('zh-CN'),
      waterTotalText: p.waterTotal.toLocaleString('zh-CN'),
      areaM2Text: Math.round(p.area * 666.6667).toLocaleString('zh-CN'),
      bdText: p.bd.toFixed(2),
      eceText: p.ece.toFixed(1),
      targetEce: 2.5,
      lr: 0.068,
      rootDepth: 0.6,
    }
  })

  const routeClass = key => (key === 'high' ? 'tag-green' : key === 'mid' ? 'tag-amber' : 'tag-orange')
  const sourceClass = type => (type.includes('标准') ? 'tag-blue' : type === '论文' ? 'tag-green' : 'tag-amber')

  const toast = (message, type = 'success') => {
    ElMessage({ message, type, duration: 2200, customClass: 'academic-message', showClose: false })
  }

  const init = () => {
    setTimeout(() => {
      loading.value = false
    }, 650)
  }

  const switchTab = (id) => {
    activeTab.value = id
  }

  const selectPlot = (id) => {
    selectedPlot.value = id
  }

  const openCalc = (id) => {
    if (id) selectedPlot.value = id
    chatOpen.value = false
    calcOpen.value = true
  }

  const closeCalc = () => {
    calcOpen.value = false
  }

  const openChat = () => {
    calcOpen.value = false
    chatOpen.value = true
  }

  const closeChat = () => {
    chatOpen.value = false
  }

  const openSource = (id) => {
    activeSourceId.value = id
    sourceOpen.value = true
  }

  const openTestPlan = () => {
    testPlanOpen.value = true
  }

  const changeScenario = (val) => {
    if (val === scenario.value) return
    scenarioLoading.value = true
    setTimeout(() => {
      scenario.value = val
      scenarioLoading.value = false
      toast(val === 'reduced' ? '已按供水上限 −25% 重算：S03–S05 淋洗受限' : '已恢复基础供水情景')
    }, 320)
  }

  const reanalyze = () => {
    reanalyzing.value = true
    scenarioLoading.value = true
    setTimeout(() => {
      reanalyzing.value = false
      scenarioLoading.value = false
      toast('已按当前情景重新分析，诊断与费用已更新')
    }, 700)
  }

  const exportReport = () => {
    exporting.value = true
    setTimeout(() => {
      const lines = [
        '# 盐碱化耕地土壤健康诊断与精准改良（原型导出）',
        '',
        `案例：${DATA.meta.caseTitle}`,
        `情景：${isReduced.value ? '供水上限 −25%（30 m³/亩·年）' : '基础供水（40 m³/亩·年）'}`,
        `预算：${DATA.meta.budgetWan} 万元 / 两年`,
        '',
        '## 分地块诊断',
        '',
        '| 地块 | pH | ECe (dS/m) | 有机质 (g/kg) | 容重 (g/cm³) | 排水 | 出苗率 (%) | 限制与建议 |',
        '|---|---|---|---|---|---|---|---|',
        ...DATA.plots.map(p => `| ${p.id} | ${p.ph.toFixed(1)} | ${p.ece.toFixed(1)} | ${p.om} | ${p.bd.toFixed(2)} | ${p.drainage} | ${p.emergence} | ${p.limits.join('、')} → ${p.rec} |`),
        '',
        '## 方案比较',
        '',
        '| 路线 | 措施 | 适用地块 | 两年费用（万元） | 适用性 | 主要限制 |',
        '|---|---|---|---|---|---|',
        ...routeList.value.map(r => `| ${r.id} ${r.name} | ${r.measures} | ${r.plots} | ${r.cost} | ${r.displaySuitability} | ${r.limits} |`),
        '',
        '## 数据缺口',
        '',
        '- ESP、SAR、CEC 未提供：钠化程度暂不可判定，石膏用量仅条件性建议。',
        '- 排水去向与水质未提供：淋洗方案需先明确去向。',
        '- 主要离子未提供：不能评价氯害/钠害。',
        '- 粪肥盐分、含水率、重金属、腐熟度未提供：材料品质待检。',
        '',
        '## 计算示例（S04）',
        '',
        'M = A × d × ρ = 26,667 m² × 0.2 m × 1.54 t/m³ = 8,213 t（干基）。',
        '',
        '> 教学模拟数据，不替代实测、法定评估或田间试验。',
      ]
      const blob = new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'soil-diagnosis-report.md'
      a.click()
      URL.revokeObjectURL(url)
      exporting.value = false
      toast('已导出 Markdown 报告（原型）')
    }, 650)
  }

  const copyCitation = async () => {
    const s = currentSource.value
    const text = `${s.title}（${s.meta}）`
    try {
      await navigator.clipboard.writeText(text)
      toast('已复制引用')
    } catch (e) {
      toast('复制失败，请手动选择文本', 'warning')
    }
  }

  const goRouteTab = () => {
    activeTab.value = 'routes'
  }

  const goSourceTab = () => {
    activeTab.value = 'sources'
  }

  const handleNav = (item) => {
    if (item.id === 'console') {
      activeTab.value = 'overview'
      return
    }
    if (item.id === 'chat') {
      openChat()
      return
    }
    if (item.id === 'library') {
      activeTab.value = 'sources'
      return
    }
    if (item.id === 'records') {
      activeTab.value = 'plan'
      return
    }
    toast(`${item.label}：原型阶段暂未接入`, 'info')
  }

  const sendChat = async () => {
    const text = chatInput.value.trim()
    if (!text || chatLoading.value) return
    chatMessages.value.push({ role: 'user', text, thinking: '' })
    chatInput.value = ''
    chatLoading.value = true
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.detail || `请求失败（${res.status}）`)
      chatMessages.value.push({
        role: 'assistant',
        text: data.answer || '（空回复）',
        thinking: data.thinking || '',
      })
    } catch (err) {
      chatMessages.value.push({
        role: 'assistant',
        error: true,
        text: `Agent 服务暂时不可用：${err.message}\n请确认 server/start.ps1 已启动，端口 8000 可访问。`,
        thinking: '',
      })
    } finally {
      chatLoading.value = false
    }
  }

  return {
    meta: ref(DATA.meta),
    plots,
    tabs,
    navGroups,
    scenarioOptions,
    routes: DATA.routes,
    sources: ref(DATA.sources),
    qc: ref(DATA.qc),
    plan: ref(DATA.plan),
    monitoring: ref(DATA.monitoring),
    testPlan: ref(DATA.testPlan),
    routeList,
    tableRows,
    eceOption,
    yieldOption,
    resourceRows,
    costRows,
    costTotal,
    budgetPct,
    budgetLeft,
    filteredSources,
    currentSource,
    selectedPlotData,
    calc,
    loading,
    scenarioLoading,
    reanalyzing,
    exporting,
    activeTab,
    selectedPlot,
    scenario,
    calcOpen,
    sourceOpen,
    testPlanOpen,
    sourceFilter,
    chatOpen,
    chatLoading,
    chatInput,
    chatMessages,
    isReduced,
    kpiWater,
    init,
    switchTab,
    selectPlot,
    openCalc,
    closeCalc,
    openChat,
    closeChat,
    openSource,
    openTestPlan,
    changeScenario,
    reanalyze,
    exportReport,
    copyCitation,
    goRouteTab,
    goSourceTab,
    handleNav,
    routeClass,
    sourceClass,
    limitClass,
    sendChat,
  }
})
