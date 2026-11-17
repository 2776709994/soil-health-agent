/* 离线原型：Vue 3 + Element Plus + ECharts，无构建步骤 */
(function () {
  const { createApp, ref, computed, watch, onMounted, onUnmounted, nextTick } = Vue;
  const { ElMessage } = ElementPlus;
  const DATA = window.CASE_DATA;

  const ICONS = {
    dashboard: '<rect x="3" y="3" width="7" height="7" rx="1.2"/><rect x="14" y="3" width="7" height="7" rx="1.2"/><rect x="3" y="14" width="7" height="7" rx="1.2"/><rect x="14" y="14" width="7" height="7" rx="1.2"/>',
    chat: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    history: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.9V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
    leaf: '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8a7 7 0 0 1-7 7z"/><path d="M2 21c0-3 1.9-5.6 5-6"/>',
    droplet: '<path d="M12 2.7s6 6.3 6 10.3a6 6 0 0 1-12 0c0-4 6-10.3 6-10.3z"/>',
    wallet: '<path d="M20 12V8H6a2 2 0 0 1 0-4h12v4"/><path d="M4 6v12a2 2 0 0 0 2 2h14v-4"/><path d="M18 12a2 2 0 0 0 0 4h4v-4z"/>',
    map: '<path d="M9 18l-6 3V6l6-3 6 3 6-3v15l-6 3z"/><path d="M9 3v15"/><path d="M15 6v15"/>',
    alert: '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    chevronDown: '<path d="m6 9 6 6 6-6"/>',
    download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>',
    refresh: '<path d="M21 12a9 9 0 0 1-9 9 9 9 0 0 1-9-9 9 9 0 0 1 9-9c2.5 0 4.8 1 6.5 2.5L21 8"/><path d="M21 3v5h-5"/>',
    calculator: '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 6h8"/><path d="M8 10h.01"/><path d="M12 10h.01"/><path d="M16 10h.01"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/>',
    external: '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    arrowRight: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    layers: '<path d="m12 2 9 5-9 5-9-5z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/>',
    flask: '<path d="M9 3h6"/><path d="M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/>',
    fileText: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8"/><path d="M8 17h8"/>',
    calendar: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    filter: '<path d="M22 3H2l8 9v7l4 2v-9z"/>',
    more: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    chart: '<path d="M3 3v18h18"/><path d="M7 16v-5"/><path d="M12 16V8"/><path d="M17 16v-3"/>',
    scale: '<path d="M12 3v18"/><path d="M5 7h14"/><path d="M7 7l-3 6h6z"/><path d="M17 7l-3 6h6z"/>',
    clipboard: '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>',
    activity: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    chevronRight: '<path d="m9 18 6-6-6-6"/>'
  };

  const AppIcon = {
    props: { name: { type: String, default: 'info' }, size: { type: [Number, String], default: 18 } },
    computed: { inner() { return ICONS[this.name] || ICONS.info; } },
    template: `<svg class="app-icon" :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" v-html="inner"></svg>`
  };

  const EChart = {
    props: { option: { type: Object, required: true }, height: { type: String, default: '220px' } },
    setup(props) {
      const el = ref(null);
      let chart = null;
      let ro = null;
      const render = () => {
        if (!el.value) return;
        if (!chart) chart = echarts.init(el.value, null, { renderer: 'svg' });
        chart.setOption(props.option, { notMerge: false, lazyUpdate: true });
      };
      onMounted(() => {
        render();
        ro = new ResizeObserver(() => { if (chart) chart.resize(); });
        ro.observe(el.value);
      });
      watch(() => props.option, render, { deep: true });
      onUnmounted(() => {
        if (ro) ro.disconnect();
        if (chart) { chart.dispose(); chart = null; }
      });
      return { el };
    },
    template: `<div ref="el" class="echart" :style="{ height }"></div>`
  };

  const CountNumber = {
    props: {
      value: { type: Number, required: true },
      duration: { type: Number, default: 520 },
      decimals: { type: Number, default: 0 }
    },
    setup(props) {
      const display = ref(0);
      let raf = 0;
      const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const animate = (from, to) => {
        if (reduced) { display.value = to; return; }
        cancelAnimationFrame(raf);
        const start = performance.now();
        const delta = to - from;
        const tick = now => {
          const t = Math.min(1, (now - start) / props.duration);
          const eased = 1 - Math.pow(1 - t, 3);
          display.value = from + delta * eased;
          if (t < 1) raf = requestAnimationFrame(tick);
        };
        raf = requestAnimationFrame(tick);
      };
      onMounted(() => animate(0, props.value));
      watch(() => props.value, (to, from) => animate(from == null ? 0 : from, to));
      onUnmounted(() => cancelAnimationFrame(raf));
      const text = computed(() => {
        const v = props.decimals ? display.value.toFixed(props.decimals) : Math.round(display.value);
        return Number(v).toLocaleString('zh-CN');
      });
      return { text };
    },
    template: `<span class="count-number">{{ text }}</span>`
  };

  const app = createApp({
    setup() {
      const loading = ref(true);
      const scenarioLoading = ref(false);
      const reanalyzing = ref(false);
      const exporting = ref(false);
      const activeTab = ref('overview');
      const mainEl = ref(null);
      const selectedPlot = ref('S04');
      const calcOpen = ref(window.innerWidth >= 1600);
      const isWide = ref(window.innerWidth >= 1600);
      const sourceOpen = ref(false);
      const activeSourceId = ref('S-02');
      const testPlanOpen = ref(false);
      const sourceFilter = ref('全部');
      const scenario = ref('base');

      const tabs = [
        { id: 'overview', label: '总览' },
        { id: 'qc', label: '数据与质控' },
        { id: 'limits', label: '限制因素' },
        { id: 'routes', label: '方案比较' },
        { id: 'cost', label: '资源与费用' },
        { id: 'plan', label: '两年计划' },
        { id: 'sources', label: '依据追溯' }
      ];

      const navGroups = [
        { label: '工作台', items: [
          { id: 'console', label: '诊断工作台', icon: 'dashboard', active: true },
          { id: 'chat', label: '对话助手', icon: 'chat' }
        ] },
        { label: '记录与知识', items: [
          { id: 'records', label: '诊断记录', icon: 'history', count: 3 },
          { id: 'library', label: '资料库', icon: 'book', count: 20 }
        ] },
        { label: '系统', items: [
          { id: 'settings', label: '设置', icon: 'settings' }
        ] }
      ];

      const scenarioOptions = [
        { value: 'base', label: '基础供水 40 m³/(亩·年)' },
        { value: 'reduced', label: '供水上限 −25% · 30 m³/(亩·年)' }
      ];

      const plots = DATA.plots;
      const selectedPlotData = computed(() => plots.find(p => p.id === selectedPlot.value) || plots[0]);
      const isReduced = computed(() => scenario.value === 'reduced');
      const kpiWater = computed(() => isReduced.value ? 30 : 40);

      const routeList = computed(() => DATA.routes.map(r => {
        const reducedTag = isReduced.value && r.id !== 'A' ? '淋洗受限' : '';
        return {
          ...r,
          scenarioTag: reducedTag,
          displaySuitability: reducedTag || r.suitability,
          displaySuitabilityKey: reducedTag ? 'conditional' : r.suitabilityKey
        };
      }));

      const limitClass = (t) => {
        if (t.includes('盐')) return 'tag-amber';
        if (t.includes('排水')) return 'tag-orange';
        if (t.includes('压实')) return 'tag-gray';
        if (t.includes('有机质')) return 'tag-blue';
        return 'tag-gray';
      };

      const tableRows = [
        { key: 'ph', label: 'pH', unit: '(1:2.5)', clickable: true, value: p => p.ph.toFixed(1) },
        { key: 'ece', label: 'ECe', unit: '(dS/m)', clickable: true, kind: 'ece' },
        { key: 'om', label: '有机质', unit: '(g/kg)', clickable: true, value: p => p.om },
        { key: 'bd', label: '容重', unit: '(g/cm³)', clickable: true, value: p => p.bd.toFixed(2) },
        { key: 'drainage', label: '排水', kind: 'tag', tags: p => [{ text: p.drainage, cls: p.drainageKey === 'good' ? 'tag-green' : p.drainageKey === 'fair' ? 'tag-amber' : 'tag-orange' }] },
        { key: 'emergence', label: '出苗率', unit: '(%)', clickable: true, value: p => p.emergence },
        { key: 'salt', label: '盐分等级', kind: 'tag', tags: p => [{ text: p.saltClass, cls: p.saltKey === 'light' ? 'tag-green' : 'tag-amber' }] },
        { key: 'sodicity', label: '钠化', kind: 'tag', tags: () => [{ text: '待测', cls: 'tag-gray' }] },
        { key: 'limits', label: '主要限制', kind: 'tag', tags: p => p.limits.map(t => ({ text: t, cls: limitClass(t) })) },
        { key: 'rec', label: '建议', kind: 'tag', tags: p => [{ text: p.rec, cls: (p.rec === '先排水' || p.rec === '分阶段') ? 'tag-orange' : 'tag-green' }] }
      ];

      const eceOption = computed(() => {
        const selected = selectedPlot.value;
        const colorOf = p => p.saltKey === 'light' ? '#7C9A72' : p.saltKey === 'moderate' ? '#C49A4A' : '#A65A3A';
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
              const p = params[0];
              return `${p.name}<br/>ECe ${Number(p.value).toFixed(1)} dS/m`;
            }
          },
          xAxis: {
            type: 'value', min: 0, max: 10, interval: 2,
            axisLabel: { color: '#8A8272', fontSize: 10 },
            splitLine: { lineStyle: { color: '#EEE7DA' } },
            axisLine: { show: false }, axisTick: { show: false }
          },
          yAxis: {
            type: 'category', inverse: true, data: plots.map(p => p.id),
            axisTick: { show: false }, axisLine: { show: false },
            axisLabel: { color: '#5C574C', fontSize: 11 }
          },
          series: [{
            type: 'bar', barWidth: 11,
            data: plots.map(p => ({
              value: p.ece,
              itemStyle: {
                color: colorOf(p),
                borderRadius: [0, 3, 3, 0],
                borderColor: p.id === selected ? '#2F4A2C' : 'transparent',
                borderWidth: p.id === selected ? 1.5 : 0
              }
            })),
            label: { show: true, position: 'right', formatter: params => Number(params.value).toFixed(1), color: '#5C574C', fontSize: 11 },
            emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(79,107,74,.22)' } },
            markLine: {
              silent: true, symbol: 'none',
              lineStyle: { color: '#B9AE99', type: 'dashed', width: 1 },
              label: { show: false },
              data: [{ xAxis: 2 }, { xAxis: 4 }, { xAxis: 8 }]
            }
          }]
        };
      });

      const yieldOption = computed(() => {
        const selected = selectedPlot.value;
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
            formatter: params => `${params[0].name}<br/>相对产量潜力 ${params[0].value}%`
          },
          xAxis: {
            type: 'category', data: plots.map(p => p.id),
            axisTick: { show: false },
            axisLine: { lineStyle: { color: '#DDD4C4' } },
            axisLabel: { color: '#5C574C', fontSize: 11 }
          },
          yAxis: {
            type: 'value', min: 0, max: 100, interval: 20,
            axisLabel: { formatter: '{value}%', color: '#8A8272', fontSize: 10 },
            splitLine: { lineStyle: { color: '#EEE7DA' } },
            axisLine: { show: false }, axisTick: { show: false }
          },
          series: [{
            type: 'bar', barWidth: 20,
            data: plots.map(p => ({
              value: p.yieldPotential,
              itemStyle: { color: p.id === selected ? '#3F5A3A' : '#7C9A72', borderRadius: [3, 3, 0, 0] }
            })),
            label: { show: true, position: 'top', formatter: '{c}%', color: '#5C574C', fontSize: 11 },
            emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(79,107,74,.22)' } }
          }]
        };
      });

      const resourceRows = computed(() => DATA.resources.map(r => {
        const supply = r.name.includes('淋洗') && isReduced.value ? 30 : r.supply;
        const demand = r.demand;
        return { ...r, supply, demand, pct: Math.round(demand / supply * 100), over: demand > supply };
      }));

      const costRows = computed(() => DATA.cost.map(c => ({ ...c, pct: Math.round(c.amount / DATA.totals.cost * 100) })));
      const costTotal = computed(() => DATA.totals.cost);
      const budgetPct = computed(() => Math.min(100, Math.round(costTotal.value / DATA.meta.budgetWan * 100)));
      const budgetLeft = computed(() => (DATA.meta.budgetWan - costTotal.value).toFixed(1));

      const currentSource = computed(() => DATA.sources.find(s => s.id === activeSourceId.value) || DATA.sources[0]);
      const filteredSources = computed(() => {
        if (sourceFilter.value === '全部') return DATA.sources;
        if (sourceFilter.value === '官方') return DATA.sources.filter(s => s.type.includes('官方'));
        return DATA.sources.filter(s => s.type === sourceFilter.value);
      });

      const calc = computed(() => {
        const p = selectedPlotData.value;
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
          rootDepth: 0.6
        };
      });

      const routeClass = (key) => key === 'high' ? 'tag-green' : key === 'mid' ? 'tag-amber' : 'tag-orange';
      const sourceClass = (type) => type.includes('标准') ? 'tag-blue' : type === '论文' ? 'tag-green' : 'tag-amber';

      const toast = (message, type = 'success') => {
        ElMessage({ message, type, duration: 2200, customClass: 'academic-message', showClose: false });
      };

      const switchTab = (id) => {
        if (activeTab.value === id) return;
        activeTab.value = id;
        nextTick(() => {
          if (mainEl.value) {
            mainEl.value.scrollTo({ top: 0, behavior: 'smooth' });
          }
          const btn = document.querySelector(`.tab[data-tab="${id}"]`);
          if (btn && btn.scrollIntoView) {
            btn.scrollIntoView({ inline: 'center', block: 'nearest', behavior: 'smooth' });
          }
        });
      };
      const selectPlot = (id) => { selectedPlot.value = id; };
      const openCalc = (id) => { selectedPlot.value = id; calcOpen.value = true; };
      const openSource = (id) => { activeSourceId.value = id; sourceOpen.value = true; };
      const openTestPlan = () => { testPlanOpen.value = true; };
      const closeCalc = () => { calcOpen.value = false; };

      const changeScenario = (val) => {
        if (val === scenario.value) return;
        scenarioLoading.value = true;
        setTimeout(() => {
          scenario.value = val;
          scenarioLoading.value = false;
          toast(val === 'reduced' ? '已按供水上限 −25% 重算：S03–S05 淋洗受限' : '已恢复基础供水情景');
        }, 320);
      };

      const reanalyze = () => {
        reanalyzing.value = true;
        scenarioLoading.value = true;
        setTimeout(() => {
          reanalyzing.value = false;
          scenarioLoading.value = false;
          toast('已按当前情景重新分析，诊断与费用已更新');
        }, 700);
      };

      const exportReport = () => {
        exporting.value = true;
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
            '> 教学模拟数据，不替代实测、法定评估或田间试验。'
          ];
          const blob = new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'soil-diagnosis-report.md';
          a.click();
          URL.revokeObjectURL(url);
          exporting.value = false;
          toast('已导出 Markdown 报告（原型）');
        }, 650);
      };

      const copyCitation = async () => {
        const s = currentSource.value;
        const text = `${s.title}（${s.meta}）`;
        try {
          await navigator.clipboard.writeText(text);
          toast('已复制引用');
        } catch (e) {
          toast('复制失败，请手动选择文本', 'warning');
        }
      };

      const goRouteTab = () => { activeTab.value = 'routes'; };
      const goSourceTab = () => { activeTab.value = 'sources'; };

      const handleNav = (item) => {
        if (item.id === 'console') { activeTab.value = 'overview'; return; }
        if (item.id === 'library') { activeTab.value = 'sources'; return; }
        if (item.id === 'records') { activeTab.value = 'plan'; return; }
        toast(`${item.label}：原型阶段暂未接入，正式版接 dsh/会话记录`, 'info');
      };

      const onKey = (e) => {
        if (e.target && e.target.closest && e.target.closest('input, textarea, select, .el-select')) return;
        if (e.key === 'Escape') {
          calcOpen.value = false;
          sourceOpen.value = false;
          testPlanOpen.value = false;
          return;
        }
        const n = Number(e.key);
        if (n >= 1 && n <= tabs.length) switchTab(tabs[n - 1].id);
      };

      const onResize = () => {
        isWide.value = window.innerWidth >= 1600;
      };

      onMounted(() => {
        window.addEventListener('keydown', onKey);
        window.addEventListener('resize', onResize);
        setTimeout(() => { loading.value = false; }, 650);
      });

      onUnmounted(() => {
        window.removeEventListener('keydown', onKey);
        window.removeEventListener('resize', onResize);
      });

      return {
        meta: DATA.meta,
        plots, tabs, navGroups, scenarioOptions,
        routeList, tableRows, eceOption, yieldOption,
        resourceRows, costRows, costTotal, budgetPct, budgetLeft,
        sources: DATA.sources, qc: DATA.qc, plan: DATA.plan, monitoring: DATA.monitoring,
        testPlan: DATA.testPlan, filteredSources, currentSource, sourceFilter,
        loading, scenarioLoading, reanalyzing, exporting,
        activeTab, mainEl, selectedPlot, selectedPlotData, calcOpen, isWide,
        sourceOpen, testPlanOpen, scenario, isReduced, kpiWater, calc,
        switchTab, selectPlot, openCalc, openSource, openTestPlan, closeCalc,
        changeScenario, reanalyze, exportReport, copyCitation,
        goRouteTab, goSourceTab, handleNav, routeClass, sourceClass, limitClass
      };
    }
  });

  app.component('app-icon', AppIcon);
  app.component('e-chart', EChart);
  app.component('count-number', CountNumber);
  app.use(ElementPlus);
  app.mount('#app');
})();
