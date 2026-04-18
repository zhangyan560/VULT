"""
埋点 T+1 定时任务 — 配置中心
65 事件 × 7 维度 × 18 事件对 × 19 跨事件比率
"""

# ──────────────────────────── 表名 ────────────────────────────

TABLE = {
    "base":       "yanzhang1.yz_event3_t1_base",
    "daily_cnt":  "yanzhang1.yz_event3_t1_daily_cnt",
    "event_log":  "ec_dwd.dwd_ec_log_di_sa_app_events",
    "underwrite": "dm_id.dm_id_risk_df_underwrite",
    "feat_a":     "yanzhang1.yz_event3_t1_feat_a",
    "feat_b":     "yanzhang1.yz_event3_t1_feat_b",
    "feat_c":     "yanzhang1.yz_event3_t1_feat_c",
    "feat_d":     "yanzhang1.yz_event3_t1_feat_d",
    "features":   "yanzhang1.yz_event3_t1_features",
}

# ──────────────────────────── 窗口 ────────────────────────────

WINDOWS = [7, 14, 28, 56, 112, 224]
ALL_WINDOW = "all"
WINDOWS_WITH_ALL = WINDOWS + [ALL_WINDOW]

MAX_LOOKBACK_DAYS = 224

# ──────────────────────────── 65 事件（四场景并集） ────────────

# key = event_code（Hive 原始值）
# alias = 去掉下划线的特征前缀

EVENT_CONFIG = {
    # ── auth 认证类（25个，首贷专用） ──
    "auth_b553_pageview":            {"alias": "authb553pageview"},
    "auth_b553_d554_click":          {"alias": "authb553d554click"},
    "auth_b553_d555_click":          {"alias": "authb553d555click"},
    "auth_b560_d561_click":          {"alias": "authb560d561click"},
    "auth_b573_pageview":            {"alias": "authb573pageview"},
    "auth_b573_d574_click":          {"alias": "authb573d574click"},
    "auth_b573_d575_click":          {"alias": "authb573d575click"},
    "auth_b573_d585_click":          {"alias": "authb573d585click"},
    "auth_b578_pageview":            {"alias": "authb578pageview"},
    "auth_b578_d579_click":          {"alias": "authb578d579click"},
    "auth_b578_d580_click":          {"alias": "authb578d580click"},
    "auth_b578_c581_d582_click":     {"alias": "authb578c581d582click"},
    "auth_b594_pageview":            {"alias": "authb594pageview"},
    "auth_b594_d595_click":          {"alias": "authb594d595click"},
    "auth_b594_d596_click":          {"alias": "authb594d596click"},
    "auth_b594_d660_click":          {"alias": "authb594d660click"},
    "auth_b597_pageview":            {"alias": "authb597pageview"},
    "auth_b597_d598_click":          {"alias": "authb597d598click"},
    "auth_b603_pageview":            {"alias": "authb603pageview"},
    "auth_b603_d604_click":          {"alias": "authb603d604click"},
    "auth_b603_d605_click":          {"alias": "authb603d605click"},
    "auth_b606_pageview":            {"alias": "authb606pageview"},
    "auth_b606_d607_click":          {"alias": "authb606d607click"},
    "auth_b606_d608_click":          {"alias": "authb606d608click"},
    "auth_next_step_result":         {"alias": "authnextstepresult"},

    # ── loan_b1 贷款主页类（12个） ──
    "loan_b1_pageview":              {"alias": "loanb1pageview"},
    "loan_b1_c140_click":            {"alias": "loanb1c140click"},
    "loan_b1_c145_click":            {"alias": "loanb1c145click"},
    "loan_b1_c148_exposure":         {"alias": "loanb1c148exposure"},
    "loan_b1_c148_d712_click":       {"alias": "loanb1c148d712click"},
    "loan_b1_c295_d711_click":       {"alias": "loanb1c295d711click"},
    "loan_b1_c2_click":              {"alias": "loanb1c2click"},
    "loan_b1_c41_d303_click":        {"alias": "loanb1c41d303click"},
    "loan_b1_c41_d304_click":        {"alias": "loanb1c41d304click"},
    "loan_b1_d709_click":            {"alias": "loanb1d709click"},
    "loan_b1_d73_click":             {"alias": "loanb1d73click"},
    "loan_first_pass_result":        {"alias": "loanfirstpassresult"},

    # ── loan_order 申请流程类（8个，复贷） ──
    "loan_order_otp_code_result":    {"alias": "loanorderotpcoderesult"},
    "loan_orderbutton_click_result": {"alias": "loanorderbuttonclickresult"},
    "loan_orderpage_display_result": {"alias": "loanorderpagedisplayresult"},
    "loan_create_order_result":      {"alias": "loancreateorderresult"},
    "loan_create_order_check_result":{"alias": "loancreateordercheckresult"},
    "loan_enter_order_check_result": {"alias": "loanenterordercheckresult"},
    "loan_order_check_step_show_result": {"alias": "loanordercheckstepshowresult"},
    "loan_b79_c552_exposure":        {"alias": "loanb79c552exposure"},

    # ── login 登录注册类（11个） ──
    "login_b70_pageview":            {"alias": "loginb70pageview"},
    "login_b70_c732_d733_click":     {"alias": "loginb70c732d733click"},
    "login_b70_c154_d155_click":     {"alias": "loginb70c154d155click"},
    "login_b70_c154_d156_click":     {"alias": "loginb70c154d156click"},
    "login_b269_pageview":           {"alias": "loginb269pageview"},
    "login_b269_d270_click":         {"alias": "loginb269d270click"},
    "login_b269_d271_click":         {"alias": "loginb269d271click"},
    "login_b222_c233_click":         {"alias": "loginb222c233click"},
    "login_login_result":            {"alias": "loginloginresult"},
    "login_register_result":         {"alias": "loginregisterresult"},
    "login_message_authorization_popup_result": {"alias": "loginmessageauthorizationpopupresult"},

    # ── general 通用类（4个） ──
    "general_switch_in_result":      {"alias": "generalswitchinresult"},
    "general_switch_out_result":     {"alias": "generalswitchoutresult"},
    "general_b718_pageview":         {"alias": "generalb718pageview"},
    "general_b396_pageview":         {"alias": "generalb396pageview"},

    # ── post 还款类（2个，复贷专有） ──
    "post_repayment_result":         {"alias": "postrepaymentresult"},
    "post_b131_c134_d135_click":     {"alias": "postb131c134d135click"},

    # ── App 生命周期（2个） ──
    "AppStart":                      {"alias": "appstart"},
    "AppEnd":                        {"alias": "append"},

    # ── 其他（1个） ──
    "other_b646_pageview":           {"alias": "otherb646pageview"},
}

ALL_EVENTS = list(EVENT_CONFIG.keys())
ALL_ALIASES = {v["alias"]: k for k, v in EVENT_CONFIG.items()}

# ──────────────────────────── 维度配置 ────────────────────────

DIM_CONFIG = {
    # Dim 1: 基础聚合
    1: {
        "aggs": ["cnt", "days", "ever", "max_daily"],
        "windows": WINDOWS_WITH_ALL,
    },
    # Dim 2: 日级统计（max_daily 与 Dim1 共用，此处不重复）
    2: {
        "aggs": ["avg_daily", "std_daily", "cv_daily", "min_daily"],
        "windows": WINDOWS_WITH_ALL,
    },
    # Dim 3: 跨窗口比率
    3: {
        "pairs": [(7, 14), (14, 28), (28, 56), (56, 112), (112, 224), (7, ALL_WINDOW)],
    },
    # Dim 4: 环比变化
    4: {
        "aggs": ["delta", "chg_rate", "accel"],
        "periods": [7, 14, 28, 56],
    },
    # Dim 5: 时序趋势
    5: {
        "point": ["days_since_last", "days_since_first"],
        "windowed": {
            "max_streak":     [7, 28, 112, 224],
            "max_gap":        [7, 28, 112, 224],
            "slope":          [28, 112],
            "ewm":            [7, 28],
            "active_gap_avg": [7, 28, 112, 224],
            "active_gap_std": [7, 28, 112, 224],
        },
    },
    # Dim 6: 时间间隔（通道 B — 走 event_log）
    6: {
        "aggs": ["intv_min", "intv_avg", "intv_max", "intv_std", "intv_cv"],
        "windows": [28, 112, 224, ALL_WINDOW],
    },
    # Dim 7: A→B 序列模式（通道 B — 走 event_log）
    7: {
        "per_pair_aggs": ["cnt", "rate", "time_avg", "time_min", "rate_chg"],
    },
}

# ──────────────────────────── Dim 7 事件对 ────────────────────

# (event_A, event_B, window_hours, label)
PAIR_CONFIG = [
    ("auth_b553_pageview",           "auth_b553_d554_click",          1,    "1h"),     # P1
    ("auth_b553_pageview",           "auth_b553_d555_click",          1,    "1h"),     # P2
    ("auth_b573_pageview",           "auth_b573_d574_click",          0.17, "10min"),  # P3
    ("auth_b573_pageview",           "auth_b594_pageview",            0.5,  "30min"),  # P4
    ("auth_b594_pageview",           "auth_b597_pageview",            48,   "48h"),    # P5
    ("auth_b597_pageview",           "auth_b606_pageview",            48,   "48h"),    # P6
    ("auth_b573_pageview",           "auth_b606_pageview",            72,   "72h"),    # P7
    ("auth_b594_pageview",           "auth_b573_pageview",            1,    "1h"),     # P8
    ("loan_b1_pageview",             "loan_b1_d709_click",            24,   "24h"),    # P9
    ("loan_b1_pageview",             "loan_orderbutton_click_result", 24,   "24h"),    # P10
    ("loan_b1_c41_d303_click",       "loan_b1_d709_click",            1,    "1h"),     # P11
    ("loan_orderpage_display_result","loan_orderbutton_click_result", 1,    "1h"),     # P12
    ("loan_orderbutton_click_result","loan_order_otp_code_result",    0.17, "10min"),  # P13
    ("loan_order_otp_code_result",   "loan_create_order_result",      0.17, "10min"),  # P14
    ("loan_first_pass_result",       "loan_b1_pageview",              168,  "7d"),     # P15
    ("post_b131_c134_d135_click",    "post_repayment_result",         1,    "1h"),     # P16
    ("post_repayment_result",        "loan_b1_pageview",              168,  "7d"),     # P17
    ("login_login_result",           "loan_b1_pageview",              1,    "1h"),     # P18
]

# Dim 7 涉及的事件（去重）
PAIR_EVENTS = list(dict.fromkeys(
    [a for a, _, _, _ in PAIR_CONFIG] + [b for _, b, _, _ in PAIR_CONFIG]
))

# ──────────────────────────── 跨事件比率（19个） ────────────────

# (feature_name, numerator_alias_col, denominator_expr)
# denominator_expr 中 {alias} 引用 Job A 输出列名
CROSS_RATIO_CONFIG = [
    # auth 认证漏斗（首贷专用）
    ("auth_retain_net_rate_all",
     "authb553d554click_cnt_all",
     "NULLIF(a.authb553d554click_cnt_all + a.authb553d555click_cnt_all, 0)"),
    ("ktp_shoot_rate_all",
     "authb573d574click_cnt_all",
     "NULLIF(a.authb573pageview_cnt_all, 0)"),
    ("ktp_to_lv_rate_all",
     "authb597pageview_cnt_all",
     "NULLIF(a.authb573pageview_cnt_all, 0)"),
    ("ktp_to_bind_rate_all",
     "authb606pageview_cnt_all",
     "NULLIF(a.authb573pageview_cnt_all, 0)"),
    ("ktp_exit_rate_all",
     "authb573d585click_cnt_all",
     "NULLIF(a.authb573pageview_cnt_all, 0)"),
    ("ktp_retry_rate_all",
     "authb594pageview_cnt_all",
     "NULLIF(a.authb573pageview_cnt_all, 0)"),
    ("lv_shoot_rate_all",
     "authb597d598click_cnt_all",
     "NULLIF(a.authb597pageview_cnt_all, 0)"),
    ("switch_ratio_7d",
     "generalswitchoutresult_cnt_7d",
     "NULLIF(a.generalswitchinresult_cnt_7d, 0)"),

    # 贷款主页漏斗（首贷②/复贷）
    ("b1_apply_rate_28d",
     "loanb1d709click_cnt_28d",
     "NULLIF(a.loanb1pageview_cnt_28d, 0)"),
    ("b1_confirm_rate_28d",
     "loanb1d73click_cnt_28d",
     "NULLIF(a.loanb1d709click_cnt_28d, 0)"),
    ("b1_adjust_rate_28d",
     "loanb1c41d303click_cnt_28d",
     "NULLIF(a.loanb1pageview_cnt_28d, 0)"),
    ("b1_exposure_rate_28d",
     "loanb1c148exposure_cnt_28d",
     "NULLIF(a.loanb1pageview_cnt_28d, 0)"),

    # 还款行为比率（复贷专用）
    ("repay_recent_ratio_7_all",
     "postrepaymentresult_cnt_7d",
     "NULLIF(a.postrepaymentresult_cnt_all, 0)"),
    ("repay_recent_ratio_28_all",
     "postrepaymentresult_cnt_28d",
     "NULLIF(a.postrepaymentresult_cnt_all, 0)"),
    ("repay_recent_ratio_112_all",
     "postrepaymentresult_cnt_112d",
     "NULLIF(a.postrepaymentresult_cnt_all, 0)"),

    # 还款页操作转化
    ("repay_click_to_result_28d",
     "postb131c134d135click_cnt_28d",
     "NULLIF(a.postrepaymentresult_cnt_28d, 0)"),

    # 登录→贷款页
    ("login_to_loan_ratio_7d",
     "loanb1pageview_cnt_7d",
     "NULLIF(a.loginloginresult_cnt_7d, 0)"),
    ("login_to_loan_ratio_28d",
     "loanb1pageview_cnt_28d",
     "NULLIF(a.loginloginresult_cnt_28d, 0)"),

    # APP切换焦虑度
    ("switch_ratio_28d",
     "generalswitchoutresult_cnt_28d",
     "NULLIF(a.generalswitchinresult_cnt_28d, 0)"),
]

# ──────────────────────────── 人群表 SQL ──────────────────────

BASE_TABLE_RISK_TYPES = (
    "'首贷还款续借','复贷还款续借','复贷打款续借','结清复贷',"
    "'循环贷','首贷风控','首贷回捞'"
)

# ──────────────────────────── 辅助函数 ────────────────────────

def event_in_clause(events=None):
    """生成 event_code IN (...) 子句"""
    evts = events or ALL_EVENTS
    return "(" + ",".join(f"'{e}'" for e in evts) + ")"


def window_cond(days_back_col: str, w) -> str:
    """生成窗口条件表达式，w 可以是 int 或 'all'"""
    if w == ALL_WINDOW:
        return f"{days_back_col} >= 1"
    return f"{days_back_col} BETWEEN 1 AND {w}"


def feat_name(alias: str, agg: str, w=None) -> str:
    """生成特征列名"""
    if w is None:
        return f"{alias}_{agg}"
    suffix = "all" if w == ALL_WINDOW else f"{w}d"
    return f"{alias}_{agg}_{suffix}"
