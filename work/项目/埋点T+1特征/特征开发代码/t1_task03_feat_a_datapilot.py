################################### 温馨提示 ###################################
# 1. PySpark 每次执行都会从头开始执行完整的代码，不分段执行
from datapilot_spark_bootstrap import spark, DataPilotUtils
# ↑ 用于初始化 SparkSession, 以及在编辑器下方【结果】区域中输出 DataFrame, 请不要删除该引用！
###############################################################################

"""
埋点 T+1 Task 03 — feat_a（Dim1-4 + Dim5 simple）
目标表：ec_risk_model.yz_event3_t1_feat_a  (~6,895 列)
依赖：Task01(base) + Task02(daily_cnt)
"""

# ══════════════════════ 配置 ══════════════════════════════════════════════════

TABLE_BASE      = "ec_risk_model.yz_event3_t1_base"
TABLE_DAILY     = "ec_risk_model.yz_event3_t1_daily_cnt"
TABLE_FEAT_WRITE = "yz_event3_t1_feat_a"

WINDOWS = [7, 14, 28, 56, 112, 224]
ALL_WINDOW = "all"
WINDOWS_WITH_ALL = WINDOWS + [ALL_WINDOW]
MAX_LOOKBACK_DAYS = 224

# DIM3 比率对
RATIO_PAIRS = [(7, 14), (14, 28), (28, 56), (56, 112), (112, 224), (7, "all")]
# DIM4 周期
DELTA_PERIODS = [7, 14, 28, 56]

# 65 个事件 {event_code: alias}
EVENT_CONFIG = {
    "auth_b553_pageview":            "authb553pageview",
    "auth_b553_d554_click":          "authb553d554click",
    "auth_b553_d555_click":          "authb553d555click",
    "auth_b560_d561_click":          "authb560d561click",
    "auth_b573_pageview":            "authb573pageview",
    "auth_b573_d574_click":          "authb573d574click",
    "auth_b573_d575_click":          "authb573d575click",
    "auth_b573_d585_click":          "authb573d585click",
    "auth_b578_pageview":            "authb578pageview",
    "auth_b578_d579_click":          "authb578d579click",
    "auth_b578_d580_click":          "authb578d580click",
    "auth_b578_c581_d582_click":     "authb578c581d582click",
    "auth_b594_pageview":            "authb594pageview",
    "auth_b594_d595_click":          "authb594d595click",
    "auth_b594_d596_click":          "authb594d596click",
    "auth_b594_d660_click":          "authb594d660click",
    "auth_b597_pageview":            "authb597pageview",
    "auth_b597_d598_click":          "authb597d598click",
    "auth_b603_pageview":            "authb603pageview",
    "auth_b603_d604_click":          "authb603d604click",
    "auth_b603_d605_click":          "authb603d605click",
    "auth_b606_pageview":            "authb606pageview",
    "auth_b606_d607_click":          "authb606d607click",
    "auth_b606_d608_click":          "authb606d608click",
    "auth_next_step_result":         "authnextstepresult",
    "loan_b1_pageview":              "loanb1pageview",
    "loan_b1_c140_click":            "loanb1c140click",
    "loan_b1_c145_click":            "loanb1c145click",
    "loan_b1_c148_exposure":         "loanb1c148exposure",
    "loan_b1_c148_d712_click":       "loanb1c148d712click",
    "loan_b1_c295_d711_click":       "loanb1c295d711click",
    "loan_b1_c2_click":              "loanb1c2click",
    "loan_b1_c41_d303_click":        "loanb1c41d303click",
    "loan_b1_c41_d304_click":        "loanb1c41d304click",
    "loan_b1_d709_click":            "loanb1d709click",
    "loan_b1_d73_click":             "loanb1d73click",
    "loan_first_pass_result":        "loanfirstpassresult",
    "loan_order_otp_code_result":    "loanorderotpcoderesult",
    "loan_orderbutton_click_result": "loanorderbuttonclickresult",
    "loan_orderpage_display_result": "loanorderpagedisplayresult",
    "loan_create_order_result":      "loancreateorderresult",
    "loan_create_order_check_result":"loancreateordercheckresult",
    "loan_enter_order_check_result": "loanenterordercheckresult",
    "loan_order_check_step_show_result": "loanordercheckstepshowresult",
    "loan_b79_c552_exposure":        "loanb79c552exposure",
    "login_b70_pageview":            "loginb70pageview",
    "login_b70_c732_d733_click":     "loginb70c732d733click",
    "login_b70_c154_d155_click":     "loginb70c154d155click",
    "login_b70_c154_d156_click":     "loginb70c154d156click",
    "login_b269_pageview":           "loginb269pageview",
    "login_b269_d270_click":         "loginb269d270click",
    "login_b269_d271_click":         "loginb269d271click",
    "login_b222_c233_click":         "loginb222c233click",
    "login_login_result":            "loginloginresult",
    "login_register_result":         "loginregisterresult",
    "login_message_authorization_popup_result": "loginmessageauthorizationpopupresult",
    "general_switch_in_result":      "generalswitchinresult",
    "general_switch_out_result":     "generalswitchoutresult",
    "general_b718_pageview":         "generalb718pageview",
    "general_b396_pageview":         "generalb396pageview",
    "post_repayment_result":         "postrepaymentresult",
    "post_b131_c134_d135_click":     "postb131c134d135click",
    "AppStart":                      "appstart",
    "AppEnd":                        "append",
    "other_b646_pageview":           "otherb646pageview",
}

# ══════════════════════ 列生成工具 ════════════════════════════════════════════

def _wc(w):
    """窗口条件：d.days_back BETWEEN 1 AND w，或 >= 1"""
    return f"d.days_back >= 1" if w == ALL_WINDOW else f"d.days_back BETWEEN 1 AND {w}"

def _wl(w):
    """窗口标签：all 或 Nd"""
    return "all" if w == ALL_WINDOW else f"{w}d"

def _fn(alias, agg, w=None):
    """特征列名"""
    if w is None:
        return f"{alias}_{agg}"
    return f"{alias}_{agg}_{_wl(w)}"

# ── Dim1: cnt / days / ever / max_daily ───────────────────────────────────
def _dim1_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for w in WINDOWS_WITH_ALL:
            wc = _wc(w)
            cols.append(f"    ,COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt ELSE 0 END),0) AS {_fn(a,'cnt',w)}")
            cols.append(f"    ,COUNT(DISTINCT CASE WHEN d.event_code='{ec}' AND {wc} THEN d.event_date END) AS {_fn(a,'days',w)}")
            cols.append(f"    ,CAST(SIGN(COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt ELSE 0 END),0)) AS INT) AS {_fn(a,'ever',w)}")
            cols.append(f"    ,MAX(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt END) AS {_fn(a,'max_daily',w)}")
    return cols

# ── Dim2: avg_daily / std_daily / cv_daily / min_daily ────────────────────
def _dim2_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for w in WINDOWS_WITH_ALL:
            wc = _wc(w)
            cnt  = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt ELSE 0 END),0)"
            days = f"NULLIF(COUNT(DISTINCT CASE WHEN d.event_code='{ec}' AND {wc} THEN d.event_date END),0)"
            sq   = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt*d.daily_cnt ELSE 0 END),0)"
            cols.append(f"    ,{cnt}/{days} AS {_fn(a,'avg_daily',w)}")
            cols.append(f"    ,SQRT(GREATEST({sq}/{days}-POW({cnt}/{days},2),0)) AS {_fn(a,'std_daily',w)}")
            cols.append(f"    ,SQRT(GREATEST({sq}/{days}-POW({cnt}/{days},2),0))/NULLIF({cnt}/{days},0) AS {_fn(a,'cv_daily',w)}")
            cols.append(f"    ,MIN(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt END) AS {_fn(a,'min_daily',w)}")
    return cols

# ── Dim3: ratio pairs ─────────────────────────────────────────────────────
def _dim3_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for ws, wl in RATIO_PAIRS:
            cnt_s = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {_wc(ws)} THEN d.daily_cnt ELSE 0 END),0)"
            cnt_l = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {_wc(wl)} THEN d.daily_cnt ELSE 0 END),0)"
            name  = f"{a}_ratio_{ws}_{_wl(wl)}"
            cols.append(f"    ,{cnt_s}/NULLIF({cnt_l},0) AS {name}")
    return cols

# ── Dim4: delta / chg_rate / accel ────────────────────────────────────────
def _dim4_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for p in DELTA_PERIODS:
            cr  = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {_wc(p)} THEN d.daily_cnt ELSE 0 END),0)"
            cd  = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {_wc(p*2)} THEN d.daily_cnt ELSE 0 END),0)"
            prev = f"({cd}-{cr})"
            cols.append(f"    ,({cr}-{prev}) AS {_fn(a,'delta',p)}")
            cols.append(f"    ,({cr}-{prev})/NULLIF({prev}+1,0) AS {_fn(a,'chg_rate',p)}")
            cols.append(f"    ,CAST(SIGN({cr}-{prev}) AS INT) AS {_fn(a,'accel',p)}")
    return cols

# ── Dim5 simple: days_since_last / days_since_first ───────────────────────
def _dim5_simple_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        cols.append(f"    ,MIN(CASE WHEN d.event_code='{ec}' THEN d.days_back END) AS {_fn(a,'days_since_last')}")
        cols.append(f"    ,MAX(CASE WHEN d.event_code='{ec}' THEN d.days_back END) AS {_fn(a,'days_since_first')}")
    return cols

# ══════════════════════ SQL 生成 ══════════════════════════════════════════════

def sql_feat_a(dt: str) -> str:
    anchor = f"'{dt}'"
    all_cols = _dim1_cols() + _dim2_cols() + _dim3_cols() + _dim4_cols() + _dim5_simple_cols()
    return f"""
INSERT OVERWRITE TABLE {TABLE_FEAT_WRITE}
    PARTITION(dt = '{dt}')
SELECT
    b.loan_account_id
{chr(10).join(all_cols)}
FROM {TABLE_BASE} b
LEFT JOIN (
    SELECT loan_account_id, event_code, event_date, daily_cnt,
           daily_cnt * daily_cnt AS daily_cnt_sq,
           DATEDIFF({anchor}, event_date) AS days_back
    FROM {TABLE_DAILY}
    WHERE event_date >= DATE_SUB({anchor}, {MAX_LOOKBACK_DAYS})
      AND event_date < {anchor}
) d ON b.loan_account_id = d.loan_account_id
WHERE b.dt = '{dt}'
GROUP BY b.loan_account_id;
"""

# ══════════════════════ 执行 ══════════════════════════════════════════════════

def process_logic():
    dt = "${p_date_iso}"
    spark.sql(sql_feat_a(dt))

if __name__ == "__main__":
    dt = "${p_date_iso}"
    print(f"[Task03] feat_a 开始，dt={dt}")
    process_logic()
    spark.stop()
    print("[Task03] feat_a 完成")
