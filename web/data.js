/* 唯一数据源：原型阶段用 JS 对象，正式版替换为 FastAPI /soil/api/* 返回值 */
window.CASE_DATA = (() => {
  const MU_M2 = 666.6667;
  const DEPTH_M = 0.2;

  const plots = [
    {
      id: 'S01', area: 40, ph: 8.5, ece: 2.1, om: 15, bd: 1.35,
      drainage: '较好', drainageKey: 'good', emergence: 82,
      saltClass: '轻度', saltKey: 'light', sodicity: '待测',
      limits: ['有机质低', '轻度盐'], rules: ['R02', 'R06', 'R05'],
      rec: 'A', recLabel: 'A 有机物料', priority: 5, status: 'normal', statusLabel: '轻度',
      note: '有机质偏低、盐分轻度；以有机物料为主，优先保苗。',
      yieldPotential: 95
    },
    {
      id: 'S02', area: 40, ph: 8.8, ece: 3.2, om: 12, bd: 1.42,
      drainage: '一般', drainageKey: 'fair', emergence: 72,
      saltClass: '轻度', saltKey: 'light', sodicity: '待测',
      limits: ['盐分', '有机质', '轻压实'], rules: ['R02', 'R06', 'R07', 'R05'],
      rec: 'A/B', recLabel: 'A/B 有机物料或炭化', priority: 4, status: 'watch', statusLabel: '关注',
      note: '轻度盐分 + 有机质低 + 轻压实；A 为主，B 可试点。',
      yieldPotential: 82
    },
    {
      id: 'S03', area: 40, ph: 9.0, ece: 4.0, om: 10, bd: 1.48,
      drainage: '一般', drainageKey: 'fair', emergence: 61,
      saltClass: '中度', saltKey: 'moderate', sodicity: '待测',
      limits: ['盐分', '有机质', '压实'], rules: ['R02', 'R06', 'R07', 'R05'],
      rec: 'B+淋洗', recLabel: 'B 炭化 + 定额淋洗', priority: 3, status: 'watch', statusLabel: '中度',
      note: '中度盐分、结构偏紧；B 路线为主，淋洗受 40 m³/亩·年约束。',
      yieldPotential: 72
    },
    {
      id: 'S04', area: 40, ph: 9.3, ece: 5.0, om: 8, bd: 1.54,
      drainage: '较差', drainageKey: 'poor', emergence: 48,
      saltClass: '中度', saltKey: 'moderate', sodicity: '待测',
      limits: ['盐分', '排水', '压实', '有机质'], rules: ['R02', 'R08', 'R07', 'R06', 'R05'],
      rec: '先排水', recLabel: '先排水，条件性改良', priority: 2, status: 'limited', statusLabel: '受限',
      note: '排水较差，淋洗前必须先明确去向并改造；钠化待测，石膏只能条件性建议。',
      yieldPotential: 60
    },
    {
      id: 'S05', area: 40, ph: 9.5, ece: 5.8, om: 6, bd: 1.60,
      drainage: '较差', drainageKey: 'poor', emergence: 36,
      saltClass: '中度', saltKey: 'moderate', sodicity: '待测',
      limits: ['盐分', '排水', '压实', '有机质'], rules: ['R02', 'R08', 'R07', 'R06', 'R05'],
      rec: '分阶段', recLabel: '先排水，分阶段', priority: 1, status: 'limited', statusLabel: '优先',
      note: '盐分最高、排水最差、容重最大；两年内以排水 + 分期淋洗 + 有机改良为主。',
      yieldPotential: 51
    }
  ].map(p => ({
    ...p,
    M: Math.round(p.area * MU_M2 * DEPTH_M * p.bd),
    perMu: Math.round(MU_M2 * DEPTH_M * p.bd),
    waterPerMu: 27.3,
    waterTotal: Math.round(0.06838 * 0.6 * p.area * MU_M2)
  }));

  const routes = [
    {
      id: 'A', name: '有机物料主导', short: '有机物料',
      measures: '腐熟粪肥 + 秸秆堆肥还田',
      plots: 'S01–S02', precondition: '粪肥腐熟；盐分、重金属、含水率合格',
      cost: '24–36', costNote: '示意',
      suitability: '高', suitabilityKey: 'high', water: '低', evidence: 'B',
      limits: '粪肥盐分可能抬高 ECe；秸秆直接还田需补氮',
      note: '优先 S01/S02，S03 可配合。'
    },
    {
      id: 'B', name: '秸秆炭化 + 定额淋洗', short: '炭化 + 淋洗',
      measures: '生物炭 + 粪肥 + 限额淋洗',
      plots: 'S02–S04', precondition: '排水可用；生物炭 pH、灰分、重金属合格',
      cost: '36–50', costNote: '示意',
      suitability: '中', suitabilityKey: 'mid', water: '中', evidence: 'B',
      limits: '生物炭偏碱，S04/S05 减量；淋洗受 40 m³/亩·年限制',
      note: 'S03 为主，S02/S04 条件性。'
    },
    {
      id: 'C', name: '钙基改良 + 排水', short: '钙基 + 排水',
      measures: '石膏/钙基 + 排水改造 + 淋洗',
      plots: 'S04–S05（条件性）', precondition: 'ESP/SAR/CEC 可得；排水去向明确；水质允许',
      cost: '50–70', costNote: '示意，可能超预算',
      suitability: '条件性', suitabilityKey: 'conditional', water: '高', evidence: 'B',
      limits: '关键参数缺失，不能给精确石膏用量；可能超 60 万元',
      note: '先补测、先排水，再决定是否施用。'
    }
  ];

  const sources = [
    {
      id: 'S-01', type: '标准', title: '农田灌溉水质标准',
      meta: 'GB 5084-2021（待核对）',
      scope: '灌溉水 ECw、盐分与水质',
      note: '用于 ECw=0.8 dS/m 的背景判断；正式版需核对条款号与适用范围。',
      status: '待核对'
    },
    {
      id: 'S-02', type: '标准', title: '土壤检测方法（pH、ECe、有机质、CEC）',
      meta: 'NY/T 1121 系列（待核对）',
      scope: 'pH 1:2.5；ECe 25℃饱和糊状土',
      note: '方法口径必须与阈值一致；EC1:5 不能直接套 ECe 分级。',
      status: '待核对'
    },
    {
      id: 'S-03', type: '标准/官方', title: '盐渍化分级与改良技术资料',
      meta: '待核对版本',
      scope: '盐分分级、钠化判定',
      note: '阈值需逐条核对，不能直接用 AI 生成值。',
      status: '待核对'
    },
    {
      id: 'P-07', type: '论文', title: '生物炭/石膏改良盐碱土研究',
      meta: '待替换为正式文献（DOI）',
      scope: '材料用量、效果、适用条件',
      note: '示例占位；答辩前换成真实论文并核对数据。',
      status: '待替换'
    },
    {
      id: 'P-12', type: '论文', title: '秸秆炭化产率与还田效应',
      meta: '待替换',
      scope: '转化产率、碳氮比',
      note: '产率按干基 25–35% 计，需文献支撑。',
      status: '待替换'
    }
  ];

  const qc = [
    { item: '单位与量纲', result: '通过', level: 'ok', detail: 'pH 1:2.5；ECe dS/m；有机质 g/kg；容重 g/cm³；出苗率 %', action: '保留' },
    { item: '缺失值', result: '5 项', level: 'warn', detail: 'ESP、SAR、CEC、排水去向、主要离子', action: '补测/调查' },
    { item: '负值与异常', result: '通过', level: 'ok', detail: '5 个地块均在合理范围', action: '—' },
    { item: 'EC 测定方法', result: '通过', level: 'ok', detail: 'ECe 25℃饱和糊状土浸提液', action: '保留' },
    { item: '钠化判定', result: '不可判定', level: 'warn', detail: '缺 ESP/SAR/CEC，不能仅凭 pH/ECe 判定', action: '补测' },
    { item: '排水条件', result: '部分缺失', level: 'warn', detail: '排水分级已有，去向与水质未提供', action: '现场调查' },
    { item: '材料品质', result: '未提供', level: 'warn', detail: '粪肥含水率、盐分、重金属、腐熟度', action: '检测' },
    { item: '出苗率', result: '仅现状', level: 'info', detail: '只能描述现状，不能作为措施效果', action: '监测' }
  ];

  const cost = [
    { item: '材料费', amount: 18.5, note: '粪肥、生物炭、石膏等（示意）' },
    { item: '运输费', amount: 4.2, note: '10/15/30 km（示意）' },
    { item: '施用/施工', amount: 7.8, note: '混拌、撒施、覆盖（示意）' },
    { item: '排水改造', amount: 16.0, note: 'S04/S05（示意）' },
    { item: '监测', amount: 6.5, note: '两年土壤/植株/排水（示意）' },
    { item: '管理及其他', amount: 5.0, note: '协调、验收、不可预见（示意）' }
  ];

  const resources = [
    { name: '玉米秸秆（干基）', supply: 80, demand: 80, unit: 't', note: '按 30% 产炭率 → 24 t 生物炭；按 3 t/ha 仅够约 3 个地块' },
    { name: '腐熟粪肥（干基）', supply: 100, demand: 100, unit: 't', note: '按 7.5 t/ha 覆盖 5 个地块；高盐地块减量' },
    { name: '额外淋洗水', supply: 40, demand: 40, unit: 'm³/(亩·年)', note: '基础情景刚好到上限；−25% 后缺口 10' }
  ];

  const plan = [
    { period: '第 1 年 Q1–Q2', title: '补测与排水', tasks: ['补测 ESP/SAR/CEC、主要离子', '明确排水去向与水质', 'S04/S05 排水改造', 'S01/S02 粪肥 + 堆肥'] },
    { period: '第 1 年 Q3–Q4', title: '改良与监测', tasks: ['S03 生物炭 + 定额淋洗', '监测 ECe/pH/ESP', '记录淋洗水量', '调整 S04/S05 措施'] },
    { period: '第 2 年 Q1–Q2', title: '补施与复测', tasks: ['补施有机物料', 'S04/S05 分阶段', '复测 ESP/SAR/CEC', '评估钠化变化'] },
    { period: '第 2 年 Q3–Q4', title: '评估与收尾', tasks: ['监测出苗率/产量', '汇总费用与水量', '形成两年报告', '提出第三年建议'] }
  ];

  const monitoring = [
    { indicator: 'ECe、pH', frequency: '每年 2 次', points: '5 个地块', purpose: '盐分/碱度变化' },
    { indicator: 'ESP、SAR、CEC', frequency: '基线 + 第 2 年', points: '5 个地块', purpose: '钠化判定' },
    { indicator: '有机质、容重', frequency: '每年 1 次', points: '5 个地块', purpose: '结构与肥力' },
    { indicator: '出苗率、产量', frequency: '每季', points: '5 个地块', purpose: '现状与效果（描述性）' },
    { indicator: '排水、水位', frequency: '每季', points: 'S04/S05', purpose: '排水与盐分去向' }
  ];

  const testPlan = [
    { item: 'ESP、SAR、CEC', purpose: '判定钠化程度；决定是否施钙基材料', method: '乙酸铵交换法 / 饱和糊状土浸提（按标准核对）', priority: '高' },
    { item: '主要离子（Na⁺、Ca²⁺、Mg²⁺、Cl⁻、HCO₃⁻）', purpose: '评价钠害、氯害与灌溉水质', method: '土壤/水常规离子分析', priority: '中' },
    { item: '排水去向与水质', purpose: '判断淋洗是否可行、是否影响受纳水体', method: '现场调查 + 排水取样', priority: '高' },
    { item: '粪肥含水率、盐分、重金属、腐熟度', purpose: '材料品质与施用量', method: '按有机肥料/农用污泥相关标准核对', priority: '中' },
    { item: '出苗率、产量', purpose: '现状描述与后续效果监测', method: '田间调查；不作为措施效果证明', priority: '低' }
  ];

  return {
    meta: { caseTitle: '西北某灌区 · 200 亩玉米田', subtitle: '5 个地块 · 两年改良方案 · 教学模拟数据', areaMu: 200, budgetWan: 60, waterCap: 40, waterReduced: 30, years: 2 },
    plots, routes, sources, qc, cost, resources, plan, monitoring, testPlan,
    totals: { cost: cost.reduce((s, c) => s + c.amount, 0) }
  };
})();
