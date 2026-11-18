"""题目二教学数据：教师给定值不得覆盖。"""

MU_M2 = 666.6667
DEPTH_M = 0.2
ROOT_DEPTH_M = 0.6
AREA_PER_PLOT_MU = 40
TOTAL_AREA_MU = 200
BUDGET_CNY = 600_000
WATER_CAP_M3_PER_MU_YEAR = 40.0
ECW_DS_M = 0.8
STRAW_T = 80.0
MANURE_T = 100.0
STRAW_BIOCHAR_YIELD = 0.30
COMPOST_YIELD = 0.50

PLOTS = [
    {
        "id": "S01", "area_mu": 40, "ph": 8.5, "ece": 2.1, "om": 15, "bd": 1.35,
        "drainage": "较好", "drainage_key": "good", "emergence": 82,
        "salt_class": "轻度", "salt_key": "light", "sodicity": "待测",
        "limits": ["有机质低", "轻度盐"], "recommendation": "A",
        "priority": 5, "status": "normal", "status_label": "轻度",
        "note": "有机质偏低、盐分轻度；以有机物料为主，优先保苗。",
    },
    {
        "id": "S02", "area_mu": 40, "ph": 8.8, "ece": 3.2, "om": 12, "bd": 1.42,
        "drainage": "一般", "drainage_key": "fair", "emergence": 72,
        "salt_class": "轻度", "salt_key": "light", "sodicity": "待测",
        "limits": ["盐分", "有机质", "轻压实"], "recommendation": "A/B",
        "priority": 4, "status": "watch", "status_label": "关注",
        "note": "轻度盐分 + 有机质低 + 轻压实；A 为主，B 可试点。",
    },
    {
        "id": "S03", "area_mu": 40, "ph": 9.0, "ece": 4.0, "om": 10, "bd": 1.48,
        "drainage": "一般", "drainage_key": "fair", "emergence": 61,
        "salt_class": "中度", "salt_key": "moderate", "sodicity": "待测",
        "limits": ["盐分", "有机质", "压实"], "recommendation": "B+淋洗",
        "priority": 3, "status": "watch", "status_label": "中度",
        "note": "中度盐分、结构偏紧；B 路线为主，淋洗受 40 m³/亩·年约束。",
    },
    {
        "id": "S04", "area_mu": 40, "ph": 9.3, "ece": 5.0, "om": 8, "bd": 1.54,
        "drainage": "较差", "drainage_key": "poor", "emergence": 48,
        "salt_class": "中度", "salt_key": "moderate", "sodicity": "待测",
        "limits": ["盐分", "排水", "压实", "有机质"], "recommendation": "先排水",
        "priority": 2, "status": "limited", "status_label": "受限",
        "note": "排水较差，淋洗前必须先明确去向并改造；钠化待测，石膏只能条件性建议。",
    },
    {
        "id": "S05", "area_mu": 40, "ph": 9.5, "ece": 5.8, "om": 6, "bd": 1.60,
        "drainage": "较差", "drainage_key": "poor", "emergence": 36,
        "salt_class": "中度", "salt_key": "moderate", "sodicity": "待测",
        "limits": ["盐分", "排水", "压实", "有机质"], "recommendation": "分阶段",
        "priority": 1, "status": "limited", "status_label": "优先",
        "note": "盐分最高、排水最差、容重最大；两年内以排水 + 分期淋洗 + 有机改良为主。",
    },
]

ROUTES = [
    {
        "id": "A", "name": "有机物料主导", "measures": "腐熟粪肥 + 秸秆堆肥还田",
        "plots": "S01–S02", "precondition": "粪肥腐熟；盐分、重金属、含水率合格",
        "cost_range_wan": [24, 36], "suitability": "高", "water": "低",
        "evidence": "B", "limits": "粪肥盐分可能抬高 ECe；秸秆直接还田需补氮",
        "note": "优先 S01/S02，S03 可配合。",
    },
    {
        "id": "B", "name": "秸秆炭化 + 定额淋洗", "measures": "生物炭 + 粪肥 + 限额淋洗",
        "plots": "S02–S04", "precondition": "排水可用；生物炭 pH、灰分、重金属合格",
        "cost_range_wan": [36, 50], "suitability": "中", "water": "中",
        "evidence": "B", "limits": "生物炭偏碱，S04/S05 减量；淋洗受 40 m³/亩·年限制",
        "note": "S03 为主，S02/S04 条件性。",
    },
    {
        "id": "C", "name": "钙基改良 + 排水", "measures": "石膏/钙基 + 排水改造 + 淋洗",
        "plots": "S04–S05（条件性）", "precondition": "ESP/SAR/CEC 可得；排水去向明确；水质允许",
        "cost_range_wan": [50, 70], "suitability": "条件性", "water": "高",
        "evidence": "B", "limits": "关键参数缺失，不能给精确石膏用量；可能超 60 万元",
        "note": "先补测、先排水，再决定是否施用。",
    },
]

SOURCES = [
    {"id": "STD-01", "type": "标准", "title": "农田灌溉水质标准（版本待核对）", "status": "待核对"},
    {"id": "STD-02", "type": "标准", "title": "土壤检测方法：pH、ECe、有机质、CEC（待核对）", "status": "待核对"},
    {"id": "STD-03", "type": "标准/官方", "title": "盐渍化分级与改良技术资料（版本待核对）", "status": "待核对"},
    {"id": "PAPER-03", "type": "论文", "title": "生物炭改良盐碱土（待替换）", "status": "待替换"},
    {"id": "PAPER-02", "type": "论文", "title": "石膏改良钠化土壤（待替换）", "status": "待替换"},
]

MISSING_FIELDS = ["ESP", "SAR", "CEC", "主要离子", "排水去向与水质", "粪肥品质"]
